import os
import time
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# ------------------------------------Load Environment Variables------------------------------------------------------------------

load_dotenv()

# --------------------------------------Initialize Google Drive API Service--------------------------------------------------------

def initialize_service():

    service_account_path = os.getenv("SERVICE_ACCOUNT_PATH")

    if not service_account_path:
        raise ValueError("SERVICE_ACCOUNT_PATH is not set in the .env file")

    creds = Credentials.from_service_account_file(service_account_path)
    service = build('drive', 'v3', credentials=creds)
    return service

# --------------------------------------------------Fetch Files in the Folder----------------------------------------------------------

def fetch_files(service, folder_id):
    query = f"'{folder_id}' in parents"
    response = service.files().list(q=query).execute()
    return {file['id']: file['name'] for file in response.get('files', [])}

# ------------------------------------------------------Re-run Your Code----------------------------------------------------------------------

def re_run_code():
    print("New file detected. Running the code...")
    # Place your code logic here
    pass

# -------------------------------------------Monitor Folder for Changes-----------------------------------------------------------------------------

def monitor_folder(folder_id):
    service = initialize_service()
    previous_files = fetch_files(service, folder_id)
    print("Monitoring folder...")
    while True:
        time.sleep(10)  # Check every 10 seconds
        current_files = fetch_files(service, folder_id)
        if len(current_files) > len(previous_files):
            new_files = set(current_files.keys()) - set(previous_files.keys())
            print(f"New files added: {', '.join([current_files[fid] for fid in new_files])}")
            re_run_code()
            previous_files = current_files

if __name__ == "__main__":
    folder_id = "1lOpqd5bYWWKUjEW8k935_i2lKAHY88wX"  #  folder ID
    monitor_folder(folder_id)
