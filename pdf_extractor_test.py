import pdfplumber


# Function to extract detailed information from the PDF and save it to a text file
def extract_detailed_data_from_pdf(pdf_file, output_file):
    with pdfplumber.open(pdf_file) as pdf:
        with open(output_file, "w", encoding="utf-8") as output:
            for page_number, page in enumerate(pdf.pages, start=1):
                output.write(f"Page {page_number}\n")
                output.write("=" * 50 + "\n")

                # Extracting raw text
                text = page.extract_text()
                if text:
                    output.write(text + "\n")
                else:
                    output.write("No text content found on this page.\n")

                # Extracting tables if available
                tables = page.extract_tables()
                if tables:
                    output.write("\nTables:\n")
                    for table_index, table in enumerate(tables, start=1):
                        output.write(f"Table {table_index}:\n")
                        for row in table:
                            output.write("\t".join(row) + "\n")

                output.write("\n" + "=" * 50 + "\n\n")


# Example usage for multiple PDFs
pdf_files = ["file1.pdf"]  # Add your list of PDF files here
for pdf_file in pdf_files:
    output_txt_file = pdf_file.replace(".pdf", "_details.txt")
    extract_detailed_data_from_pdf(pdf_file, output_txt_file)
    print(f"Extracted data from {pdf_file} and saved to {output_txt_file}")
