import pdfplumber
import re
from pymongo import MongoClient


def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"
    return extracted_text


def extract_name(text):
    name_match = re.search(r'Name:\s*(.*)', text)
    if name_match:
        return name_match.group(1).strip()
    return None

def extract_email(text):
    email_match = re.search(r'Email:\s*([^\s]+)', text)
    if email_match:
        return email_match.group(1).strip()
    return None

def extract_contact_number(text):
    contact_match = re.search(r'Contact Number:\s*([\d ]+)', text)
    if contact_match:
        return contact_match.group(1).strip()
    return None

def extract_education(text):
    edu_match = re.search(r'Education:\s*(.*)', text)
    if edu_match:
        return edu_match.group(1).strip()
    return None

def extract_degree(text):
    degree_match = re.search(r'Degree:\s*(.*)', text)
    if degree_match:
        return degree_match.group(1).strip()
    return None

def extract_skills(text):
    skills_match = re.search(r'Skills:\s*(.*)', text)
    if skills_match:
        return skills_match.group(1).strip().split(', ')
    return []

def extract_soft_skills(text):
    soft_skills_match = re.search(r'Soft skills:\s*(.*)', text)
    if soft_skills_match:
        return soft_skills_match.group(1).strip().split(', ')
    return []

def extract_experience(text):
    exp_match = re.search(r'Experience:\s*(.*)', text)
    if exp_match:
        return exp_match.group(1).strip()
    return None


def connect_to_mongodb():
    client = MongoClient('mongodb+srv://manesha:miel%401102@cluster0.1g6gr2u.mongodb.net/')  
    db = client['AI_Project']  
    return db['users']   


pdf_path = r"C:\Users\Manesha's Notebook\OneDrive\Desktop\CV_Chatbot\CV_Chatbot\temp.pdf" 


extracted_text = extract_text_from_pdf(pdf_path)


name = extract_name(extracted_text)
email = extract_email(extracted_text)
contact_number = extract_contact_number(extracted_text)
education = extract_education(extracted_text)
degree = extract_degree(extracted_text)
skills = extract_skills(extracted_text)
soft_skills = extract_soft_skills(extracted_text)
experience = extract_experience(extracted_text)


cv_data = {
    "name": name,
    "email": email,
    "contact_number": contact_number,
    "education": education,
    "degree": degree,
    "skills": skills,
    "soft_skills": soft_skills,
    "experience": experience
}


collection = connect_to_mongodb()
result = collection.insert_one(cv_data)  


print("Data has been stored....")
