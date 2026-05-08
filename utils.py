import pdfplumber
import re

# Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text


# Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub('[^a-z ]', ' ', text)
    return text