# Download PDF file
import os
from operator import lshift
import requests
import pandas as pd
# Get PDF document
# pdf_path = "./Data/Data_pdf/vietcom11.pdf"
pdf_path = "./Data/Data_pdf/vietcom14.pdf"

# Download PDF if it doesn't already exist
if not os.path.exists(pdf_path):
  print("File doesn't exist, downloading...")
else:
  print(f"File {pdf_path} exists.")

# Requires !pip install PyMuPDF, see: https://github.com/pymupdf/pymupdf
import fitz # (pymupdf, found this is better than pypdf for our use case, note: licence is AGPL-3.0, keep that in mind if you want to use any code commercially)
from tqdm.auto import tqdm # for progress bars, requires !pip install tqdm

def text_formatter(text: str) -> str:
    """Performs minor formatting on text."""
    cleaned_text = text.replace("\n", " ").strip() # note: this might be different for each doc (best to experiment)

    # Other potential text formatting functions can go here
    return cleaned_text

# Open PDF and get lines/pages
# Note: this only focuses on text, rather than images/figures etc
def open_and_read_pdf(pdf_path: str) -> list[dict]:
    """
    Opens a PDF file, reads its text content page by page, and collects statistics.

    Parameters:
        pdf_path (str): The file path to the PDF document to be opened and read.

    Returns:
        list[dict]: A list of dictionaries, each containing the page number
        (adjusted), character count, word count, sentence count, token count, and the extracted text
        for each page.
    """
    doc = fitz.open(pdf_path)  # open a document
    pages_and_texts = []
    for page_number, page in tqdm(enumerate(doc)):  # iterate the document pages
        text = page.get_text()  # get plain text encoded as UTF-8
        text = text_formatter(text)
        # pages_and_texts.append({"page_number": page_number+1,  # adjust page numbers since our PDF starts on page 42
        #                         "page_char_count": len(text),
        #                         "page_word_count": len(text.split(" ")),
        #                         "page_sentence_count_raw": len(text.split(". ")),
        #                         "page_token_count": len(text) / 4,  # 1 token = ~4 chars, see: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
        #                         "text": text})
        pages_and_texts.append({"page_number": page_number+1,  # adjust page numbers since our PDF starts on page 42
                                "page_char_count": len(text),
                                "page_word_count": len(text.split(" ")),
                                "page_sentence_count_raw": len(text.split(". ")),
                                "page_token_count": len(text) / 4,  # 1 token = ~4 chars, see: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
                                "text": text})
    return pages_and_texts


pages_and_texts = open_and_read_pdf(pdf_path=pdf_path)

import pandas as pd

# Strings to remove
strings_to_remove = ["Số tài khoản: 0011001932418 STT NGÀY GIAO  DỊCH SỐ TIỀN GHI  CÓ DIỄN GIẢI "
]

# Function to remove specified strings
def clean_text(text, strings_to_remove):
    for string in strings_to_remove:
        text = text.replace(string, "")
    return text.strip()

# Cleaning the texts
pages_and_texts = [{'page_number': p['page_number'], 'text': clean_text(p['text'], strings_to_remove)} for p in pages_and_texts]

import re # Extracting text data from the pages
text_data = [page['text'] for page in pages_and_texts]

# Combining all texts into one string
combined_text = ' '.join(text_data)
# Define a regex pattern to extract the records
pattern = r'(\d{2}/\d{2}/\d{4}) +([\d.]+) (.+?)(?=\d{2}/\d{2}/\d{4}|$)'
matches = re.findall(pattern, combined_text)

# Convert matches to DataFrame
data = []
for match in matches:
    data.append([match[0], match[1], match[2]])

# Create DataFrame
df = pd.DataFrame(data, columns=['Date', 'Money', 'Description'])
df.to_csv("./Data/Data_csv/vietcom14.csv", index=False)