import fitz  # PyMuPDF


def pdf_to_text(pdf_path, txt_path):
    """
    Reads a PDF file and writes its content to a text file.

    :param pdf_path: Path to the PDF file.
    :param txt_path: Path to the output text file.
    """
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        print(f"Opened PDF file: {pdf_path}")

        # Open the text file for writing
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            # Iterate through the pages
            for page_number in range(len(pdf_document)):
                # Get the page
                page = pdf_document.load_page(page_number)
                # Extract text from the page
                text = page.get_text()
                # Write the text to the file
                txt_file.write(f"Page {page_number + 1}:\n")
                txt_file.write(text)
                txt_file.write("\n" + "-" * 80 + "\n")

        print(f"PDF content has been written to {txt_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the PDF document is closed
        pdf_document.close()


# Example usage
pdf_path = "resources/helper-functions/testing_library/sample1.pdf"
txt_path = "resources/helper-functions/testing_library/output.txt"
pdf_to_text(pdf_path, txt_path)


# start_word = "compiler"  # Replace with the start word
# end_word = "crashing"  # Replace with the end word
# extract_text_from_pdf(pdf_path, output_txt_path, start_word, end_word)
