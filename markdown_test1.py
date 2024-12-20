import os
import io
import psutil  # For monitoring memory and CPU usage
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import markdownify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Load environment variables
load_dotenv()

# Set up Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = ''       #----------------------Add the path to the service account file--------------------------------

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Function to log system resource usage
def log_resource_usage(step):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    print(f"[{step}] Memory Usage: {memory_info.rss / (1024 * 1024):.2f} MB | CPU Usage: {cpu_percent:.2f}%")

# Function to convert PDF content to Markdown
def convert_pdf_to_markdown(pdf_content):
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        markdown_text = markdownify.markdownify(text)
        return markdown_text
    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")
        return None

# Function to upload Markdown to Google Drive
def upload_markdown_to_drive(markdown_content, filename, folder_id):
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

# Main function to process CVs
def download_and_convert_cvs_and_upload():
    source_folder_id = '1pd3FKMd-3Vm7hESaerxAyGzoOJa7LxZX'  # CV_Storage folder ID
    target_folder_id = '19-gSAcIxRTe6u5r6jv0HyUSGAkgilKgS'  # Markdown_Cvs folder ID

    # Log initial resource usage
    log_resource_usage("Start of script")

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
            # Log resource usage before downloading
            log_resource_usage(f"Before downloading {file_name}")

            # Download the PDF
            request = drive_service.files().get_media(fileId=file_id)
            pdf_content = request.execute()
            if not pdf_content:
                print(f"Failed to download {file_name}.")
                continue

            # Log resource usage after downloading
            log_resource_usage(f"After downloading {file_name}")

            # Convert PDF to Markdown
            markdown_content = convert_pdf_to_markdown(pdf_content)
            if not markdown_content:
                print(f"Failed to convert {file_name} to Markdown.")
                continue

            # Log resource usage after conversion
            log_resource_usage(f"After converting {file_name} to Markdown")

            # Upload Markdown to Google Drive
            markdown_filename = f"{os.path.splitext(file_name)[0]}.md"
            upload_markdown_to_drive(markdown_content, markdown_filename, target_folder_id)

            # Log resource usage after uploading
            log_resource_usage(f"After uploading {file_name}")

        except Exception as e:
            print(f"Error processing file {file_name}: {e}")

    # Log final resource usage
    log_resource_usage("End of script")


if __name__ == "__main__":
    print("Downloading CVs, converting to Markdown, and uploading to Google Drive...")
    download_and_convert_cvs_and_upload()
