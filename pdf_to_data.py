import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()

import fitz  
from transformers import pipeline

pdf_path = r"C:\Users\Manesha's Notebook\OneDrive\Desktop\CV_Chatbot\CV_Chatbot\temp.pdf" 

if os.path.exists(pdf_path):
    print("File exists. Proceeding with extraction...")
else:
    print("File does not exist. Please check the path.")


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text


pdf_text = extract_text_from_pdf(pdf_path)


summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")  


summary = summarization_pipeline(pdf_text, max_length=150, min_length=50, do_sample=False)


print("Summary of the PDF:")
print(summary[0]['summary_text'])
