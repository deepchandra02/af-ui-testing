# Deep Chandra
# deepc

import ImageWriter

# function that converts an image to black and white

def convertBlackWhite(pic):

# getting dimensions of image
    rows = ImageWriter.getHeight(pic)
    columns = ImageWriter.getWidth(pic)
    
# going pixel by pixel    
    for i in range(0,rows):
        for j in range(0,columns):
            c = ImageWriter.getColor(pic,j,i)     # get the rgb values
            
            if sum(c)/3 >= 100:     # comapring the avg
                ImageWriter.setColor(pic,j,i,[255,255,255]) # white
            else:
                ImageWriter.setColor(pic,j,i,[0,0,0]) # black

    
    ImageWriter.updatePicture(pic) # updates picture to reflect changes
# end of function


# helper function to start removing the border
# either from the left or the right side of the 
# picture, depending on the arguments passed
    
def remover(pic,s1,s2,i,f1,f2):
# s1 - start value of loop for height
# s2 - start value of loop for width
# f1 - finish value of loop for height
# f2 - finish value of loop for width
# i - interval for loop. 1 for starting from left, -1 for right

    for y in range(s1,f1,i):
        currentCol = ImageWriter.getColor(pic,0,y)
        
    # this is to account for 2 cases in images
        if currentCol == [0,0,0]:
            flag = 1    # if the first pixel is part of the border
        else:
            flag = 0    # if the first pixel is not part of the border
            
        for x in range(s2,f2,i):
        
        # keeping track of no. of times colour of pixel changes
            if (currentCol != ImageWriter.getColor(pic,x,y)):
                flag += 1
                currentCol = ImageWriter.getColor(pic,x,y)
                
        # if there are more than 2 changes, it means we reached the
        # end of the border and its time to go to next ro
            if (flag == 2):
                break
            
        # change black pixels of border to white
            if([ImageWriter.getColor(pic,x,y) == 0,0,0]):
                ImageWriter.setColor(pic,x,y,[255,255,255])
    
    ImageWriter.updatePicture(pic) # updates picture to reflect changes
# end of function
 
    
# function that removes the border from the image

def removeBorder(pic):
    
# getting dimensions of image
    w = ImageWriter.getWidth(pic)
    h = ImageWriter.getHeight(pic)
    
# removing border - starting from the left
    remover(pic,0,0,1,h,w)

# removing border - starting from the left    
    remover(pic,h-1,w-1,-1,0,0)
    
    ImageWriter.updatePicture(pic) # updates picture to reflect changes
# end of function


# function that determines position of the Arabic numbers on 
# the license plate and send the top and bottom row values of
# the area of license plate that holds the numbers

def horizontalSegmentation(pic):
    
# initialize variables
    inBlob = False
    startOfBlob = maxBlob = 0
    result = []
    black = [0,0,0]
     

# loop through all rows of the image
    for y in range(ImageWriter.getHeight(pic)):
        
        flag = False    # black pixel indicator for a row
        
        for x in range(ImageWriter.getWidth(pic)):
        
        # check if there are any black pixels in this row
            if (ImageWriter.getColor(pic,x,y) == black):
                flag = True
                
    # if black pixels found and inBlob is False
        if (flag == True and inBlob == False):
            inBlob = True       # this is start of a blob
            startOfBlob = y     # row value of top of blob
        
    # if no black pixels are found and inBlob is True
        elif(flag == False and inBlob == True):
            inBlob = False      # this is end of the blob
            size = y - startOfBlob # calculate size of current blob
            
            if size > maxBlob:  # if this is the biggest blob
            # row values of top and bottom of blob
                result = [startOfBlob, y]
                maxBlob = size
    
    return result
# end of function
    

# function that goes through the number segment in
# the license plate and determines the start and end column values of
# the area of license plate that holds the numbers

def verticalSegmentation(pic,startRow,endRow,col):

# initialize variables
    inDigit = False
    startOfDigit = 0
    result, black = [], [0,0,0]

# loop through all columns of the image between startRow and endRow
    for x in range(col,ImageWriter.getWidth(pic)):

        flag = False    # black pixel indicator for a row
        for y in range(startRow,endRow):
        
        # check if there are any black pixels in this column
            if (ImageWriter.getColor(pic,x,y) == black):
                flag = True
                break
            
            
    # if black pixels found and inDigit is False
        if (flag == True and inDigit == False):
        # this is start of a possible digit
            inDigit = True    
        # column value of start of the block of pixels
            startOfDigit = x
        
    # if no black pixels are found and inDigit is True
        elif(flag == False and inDigit == True):
            inDigit = False         # this is end of the block of pixels
            size = x - startOfDigit # calculate size of block
        
            if size > 5:  # if this is a digit
            # column values of start and end of digit
                result = [startOfDigit, x]
                return result
    return False
# end of function        


# helper function that finds the percentage of black pixels in a
# given quadrant
    
def quadPercent(pic,r1,r2,c1,c2):
    totPixels = blackPixels = 0
    
    for y in range(r1,r2):
        for x in range(c1,c2):
            totPixels += 1
            
            if (ImageWriter.getColor(pic,x,y) == [0,0,0]):
                blackPixels += 1
    return blackPixels/totPixels
# end of function
          
    
# helper function to find and return the overall 
# difference in quadrant values

def totDiff(a,b,c,d,a1,b1,c1,d1):
    
    diff1 = abs(a-a1)
    diff2 = abs(b-b1)
    diff3 = abs(c-c1)
    diff4 = abs(d-d1)
    
    return ((diff1 + diff2 + diff3 + diff4)/4)
# end of function    


# function that decodes the numerical value of the image 
# of the arabic numeral

def decodeCharacter(pic,startRow,endRow,startCol,endCol):
    
# list to store the values of total difference
    diffList = []
    
# lists that store the expected quadrant values of each number
# correspoding to index position
    q1K = [0.21,0.16,0.38,0.47,0.10,0.52,0.45,0.33,0.22,0.52]
    q2K = [0.31,0.58,0.80,0.58,0.58,0.37,0.44,0.37,0.26,0.80]
    q3K = [0.27,0.12,0.33,0.34,0.72,0.59,0.04,0.25,0.40,0.22]
    q4K = [0.26,0.54,0.23,0.00,0.32,0.51,0.43,0.25,0.36,0.55]

# to get the middle row and column values to be able to form quadrants
    midRow = (startRow + endRow)//2
    midCol = (startCol + endCol)//2

# percentage of black pixels in each quadrant of the current digit
# of the input pic    
    q1 = quadPercent(pic,startRow,midRow,midCol,endCol)
    q2 = quadPercent(pic,startRow,midRow,startCol,midCol)
    q3 = quadPercent(pic,midRow,endRow,startCol,midCol)
    q4 = quadPercent(pic,midRow,endRow,midCol,endCol)
    
# comparing quadrant values with the given values for digits 0 to   9    
    for i in range(10):
        diffList += [totDiff(q1,q2,q3,q4,q1K[i],q2K[i],q3K[i],q4K[i])]
        
# we get the minimum difference, and check its index
# the corresponding index must be the digit, and so we return it
    return diffList.index(min(diffList))
# end of function
        

# funtion that takes the pic of a license plate and returns the number
# represented in the image

def decodeLicensePlate(filename):

# final list that will hold the decoded digits of the license plate
    final = []

# loading the image
    pic = ImageWriter.loadPicture(filename)  
    
# converts the image to black and white
    convertBlackWhite(pic)
    
# removes the border around the image
    removeBorder(pic)

# store the starting and end row values in the image 
# where the numbers are present
    rowLim = horizontalSegmentation(pic)
    
# we initially start searching for digits from column 0    
    col = 0
# repeating the decoding process for each digits
    while(True):

    # store the starting and end column values of the current
    # digit being decoded
        colLim = verticalSegmentation(pic,rowLim[0],rowLim[1],col)
    
    # if colLim is false, it means there are no more digits
        if (colLim == False):
            break
    # get the decoded int value of the character
        ans = decodeCharacter(pic,rowLim[0]-1,rowLim[1],colLim[0],colLim[1])
    
    # adding to the final list of license plate numbers as a string
        final += [str(ans)]
    
    # assigning the column after which the next character is to be decoded    
        col = colLim[1]
        
# return the license plate number as a string        
    return ''.join(final)
# end of function

pic = "p7.bmp"
print(decodeLicensePlate(pic))