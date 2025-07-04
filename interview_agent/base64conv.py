import base64

def encode_pdf_to_base64(pdf_path):
    """
    Reads a PDF file from the given path and returns its Base64-encoded string.
    
    :param pdf_path: Path to the PDF file.
    :return: Base64-encoded string of the PDF content.
    """
    try:
        with open(pdf_path, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")
        return encoded_string
    except Exception as e:
        print(f"Error encoding PDF: {e}")
        return None
