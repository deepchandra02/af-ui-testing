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


def detectLineSeparator(pic, sectionStartRow, rows, cols):
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


def cropSections(
    original_image_path, sections, output_directory, base_filename, isTitle
):
    """
    Crops the original image into the given sections and saves them in a single directory.
    :param original_image_path: Path to the original image.
    :param sections: List of [start_y, end_y] tuples for cropping.
    :param output_directory: Directory to save the cropped images.
    :param base_filename: The base filename to append section names.
    """
    os.makedirs(output_directory, exist_ok=True)

    original_image = cv2.imread(original_image_path)
    height, width, _ = original_image.shape

    for index, (start_y, end_y) in enumerate(sections):
        cropped_image = original_image[start_y:end_y, 0:width]

        if index == 0 and isTitle:
            section_name = "title"
        else:
            section_name = f"section_{index}"

        output_path = os.path.join(
            output_directory, f"{base_filename}_{section_name}.jpg"
        )
        cv2.imwrite(output_path, cropped_image)
        print(f"Saved: {output_path}")


def process_form_images(input_directory):
    output_directory = f"{input_directory}_all_sections"
    os.makedirs(output_directory, exist_ok=True)  # Create a single output folder
    isTitle = True
    # Iterate over all images in the directory
    for filename in sorted(os.listdir(input_directory)):
        if filename.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):  # Ensure it's an image file
            input_image_path = os.path.join(input_directory, filename)

            # Load the image
            image = ImageWriter.loadPicture(input_image_path)
            convertBlackWhite(image)
            rows = ImageWriter.getHeight(image)
            cols = ImageWriter.getWidth(image)
            print(f"Processing {filename} - Rows: {rows}, Cols: {cols}")

            # Detect positions of sections
            sections = detectLineSeparator(image, 0, rows, cols)
            print(f"Detected sections: {sections}")

            # Crop and save sections in a single directory
            base_filename = os.path.splitext(filename)[
                0
            ]  # Extract filename without extension
            cropSections(
                input_image_path, sections, output_directory, base_filename, isTitle
            )
        isTitle = False

    print(f"Segmentation complete. All results saved in {output_directory}")


# # Usage
input_directory = "gpt-train/file1"
process_form_images(input_directory)
