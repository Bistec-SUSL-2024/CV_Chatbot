from langchain.text_splitter import RecursiveCharacterTextSplitter
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io
import os

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

FOLDER_ID = '1whaChKzr1JpKV_O7rxkFQJzaNWy2sPKG'

query = f"'{FOLDER_ID}' in parents and mimeType='text/markdown'"
results = drive_service.files().list(q=query, fields="files(id, name)").execute()
files = results.get('files', [])

if not files:
    print("No markdown files found in the folder.")
else:
    print(f"Found {len(files)} markdown files.")
    markdown_texts = []

    for file in files:
        file_id = file['id']
        file_name = file['name']

        
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        markdown_text = fh.read().decode('utf-8')
        markdown_texts.append(markdown_text)
        print(f"Downloaded: {file_name}")

    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    for markdown_text in markdown_texts:
        chunks = text_splitter.create_documents([markdown_text])
        for chunk in chunks:
            print(chunk)
