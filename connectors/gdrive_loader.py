import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GDriveLoader:
    def __init__(self, credentials_path='credentials.json'):
        self.creds = None
        self.credentials_path = credentials_path
        self.service = self._authenticate()

    def _authenticate(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        return build('drive', 'v3', credentials=self.creds)

    def list_files(self, folder_id=None):
        if not self.service:
            return []
        
        # Query for PDFs, Google Docs, and Text files
        query = ("mimeType='application/pdf' or "
                 "mimeType='application/vnd.google-apps.document' or "
                 "mimeType='text/plain'")
        
        if folder_id:
            query = f"'{folder_id}' in parents and ({query})"
        
        results = self.service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        return results.get('files', [])

    def download_file(self, file_id, file_name, mime_type, dest_folder='data/docs'):
        if not self.service:
            return None
        
        os.makedirs(dest_folder, exist_ok=True)
        
        # If it's a Google Doc, we must export it as a PDF
        if mime_type == 'application/vnd.google-apps.document':
            request = self.service.files().export_media(fileId=file_id, mimeType='application/pdf')
            file_name += ".pdf"
        else:
            request = self.service.files().get_media(fileId=file_id)
        
        dest_path = os.path.join(dest_folder, file_name)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        with open(dest_path, 'wb') as f:
            f.write(fh.getvalue())
        
        return dest_path
