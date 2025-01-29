import ImageWriter
import cv2
import os


#  Functions
def convertBlackWhite(pic):

    # getting dimensions of image
    rows = ImageWriter.getHeight(pic)
    columns = ImageWriter.getWidth(pic)

    # going pixel by pixel
    for i in range(0, rows):
        for j in range(0, columns):
            c = ImageWriter.getColor(pic, j, i)  # get the rgb values

            if sum(c) / 3 >= 100:  # comparing the avg
                ImageWriter.setColor(pic, j, i, [255, 255, 255])  # white
            else:
                ImageWriter.setColor(pic, j, i, [0, 0, 0])  # black


def detectLineSeparator(pic, sectionStartRow):
    global rows
    global cols
    # initialize variables
    sectionEndRow = rows
    expectedLineProportion = 0.7
    lineStartX = 0
    lineStartY = 0
    lineWidth = 0
    result, black = [], [0, 0, 0]

    # loop through all rows of the image (along y-axis)
    for y in range(sectionStartRow, rows):
        flag = False  # black pixel indicator for a row
        for x in range(0, cols):
            # check if there are any black pixels in this
            if ImageWriter.getColor(pic, x, y) == black:
                if flag == False:
                    lineStartX = x
                    lineStartY = y
                    lineWidth = 0
                    flag = True
                else:
                    lineWidth += 1
            else:
                if flag == True:
                    flag = False
                    if lineWidth > expectedLineProportion * cols:
                        print("Line", lineStartX, lineStartY)
                        sectionEndRow = y
                        result.append([sectionStartRow, sectionEndRow])
                        sectionStartRow = sectionEndRow
                        break
    if result[-1][1] != rows:
        result.append([result[-1][1], rows])
    return result


def cropSections(original_image_path, sections, output_directory):
    """
    Crops the original image into the given sections and saves them.
    :param original_image_path: Path to the original image.
    :param sections: List of [start_y, end_y] tuples for cropping.
    :param output_directory: Directory to save the cropped images.
    """
    os.makedirs(output_directory, exist_ok=True)

    original_image = cv2.imread(original_image_path)
    height, width, _ = original_image.shape

    for index, (start_y, end_y) in enumerate(sections):
        cropped_image = original_image[start_y:end_y, 0:width]
        output_path = os.path.join(output_directory, f"section_{index + 1}.jpg")
        cv2.imwrite(output_path, cropped_image)
        print(f"Saved: {output_path}")


def cropSections(original_image_path, sections, output_directory):
    """
    Crops the original image into the given sections and saves them.
    :param original_image_path: Path to the original image.
    :param sections: List of [start_y, end_y] tuples for cropping.
    :param output_directory: Directory to save the cropped images.
    """
    global cols
    image = cv2.imread(original_image_path)
    for index, (start_y, end_y) in enumerate(sections):
        cropped_image = image[start_y:end_y, 0:cols]
        output_path = os.path.join(output_directory, f"section_{index + 1}.jpg")
        cv2.imwrite(output_path, cropped_image)
        print(f"Saved: {output_path}")


# Usage
input_image_path = "gpt-train/page1.jpg"
output_directory = "gpt-train/images"
os.makedirs(output_directory, exist_ok=True)

# Load the image
image = ImageWriter.loadPicture(input_image_path)
pictureForProcessing = image
convertBlackWhite(pictureForProcessing)
rows = ImageWriter.getHeight(pictureForProcessing)
cols = ImageWriter.getWidth(pictureForProcessing)
print(f"Rows: {rows}, Cols: {cols}")

# Detect positions of sections
sections = detectLineSeparator(pictureForProcessing, 0)

print(sections)

cropSections(input_image_path, sections, output_directory)
