import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract plain text from a PDF given its raw bytes.
    Joins all pages into a single string.
    Raises ValueError if the PDF yields no text (e.g. scanned image-only PDF).
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    pages_text = []
    for page in doc:
        pages_text.append(page.get_text("text"))   # "text" = plain text mode

    full_text = "\n".join(pages_text).strip()

    if not full_text:
        raise ValueError(
            "No text could be extracted from the PDF. "
            "It may be a scanned image. Please upload a text-based PDF."
        )

    return full_text