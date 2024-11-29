import os
import io
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import markdownify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


load_dotenv()


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'Service-Account_file/peak-bebop-442908-v8-3f16757fc419.json'  

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def convert_pdf_to_markdown(pdf_content):
    """Convert PDF content to Markdown format."""
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        markdown_text = markdownify.markdownify(text)
        return markdown_text
    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")
        return None

def upload_markdown_to_drive(markdown_content, filename, folder_id):
    """Upload Markdown content to a specific Google Drive folder."""
    file_metadata = {
        'name': filename,  
        'parents': [folder_id],  
        'mimeType': 'text/markdown'
    }
    
    media = MediaIoBaseUpload(io.BytesIO(markdown_content.encode("utf-8")), mimetype='text/markdown')

    try:
        drive_service.files().create(body=file_metadata, media_body=media).execute()
        print(f"Successfully uploaded {filename} to Google Drive folder.")
    except Exception as e:
        print(f"Error uploading {filename} to Google Drive: {e}")

def download_and_convert_cvs_and_upload():
    """Fetch CVs from Google Drive, convert them to Markdown, and upload to a different folder."""
    source_folder_id = '1pd3FKMd-3Vm7hESaerxAyGzoOJa7LxZX'  #  CV_Storage folder ID
    target_folder_id = '19-gSAcIxRTe6u5r6jv0HyUSGAkgilKgS'  #  Markdown_Cvs folder ID

    # List files in the source folder
    results = drive_service.files().list(
        q=f"'{source_folder_id}' in parents and mimeType='application/pdf'",
        pageSize=10,
        fields="files(id, name)"
    ).execute()

    if not results.get('files', []):
        print("No PDF files found in the specified folder.")
        return

    for file in results.get('files', []):
        file_id = file['id']
        file_name = file['name']
        print(f"Processing file: {file_name} (ID: {file_id})")

        try:
            
            request = drive_service.files().get_media(fileId=file_id)
            pdf_content = request.execute()
            if not pdf_content:
                print(f"Failed to download {file_name}.")
                continue

            
            markdown_content = convert_pdf_to_markdown(pdf_content)
            if not markdown_content:
                print(f"Failed to convert {file_name} to Markdown.")
                continue

            
            markdown_filename = f"{os.path.splitext(file_name)[0]}.md"
            upload_markdown_to_drive(markdown_content, markdown_filename, target_folder_id)

        except Exception as e:
            print(f"Error processing file {file_name}: {e}")


if __name__ == "__main__":
    print("Downloading CVs, converting to Markdown, and uploading to Google Drive...")
    download_and_convert_cvs_and_upload()
