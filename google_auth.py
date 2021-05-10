import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import file_processing as fp
from io import BytesIO
import shutil

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_filter_function(isFolder):
    filetype = 'application/vnd.google-apps.folder' if isFolder else 'application/octet-stream'

    def filter_content(file):
        return file['mimeType'] == filetype
    return filter_content


class GoogleAuth:
    def __init__(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        self.service = build('drive', 'v3', credentials=creds)

    def get_list(self, folder_name):
        query = f"(mimeType='application/vnd.google-apps.folder' or mimeType='application/octet-stream') and ('{folder_name}' in parents "
        if folder_name == 'root':
            query = query + 'or sharedWithMe'
        query = query + ')'
        result = self.service.files().list(
            q=query,
            fields='files(id, name, mimeType)'
        ).execute()
        items = result.get('files', [])
        files = sorted(list(filter(get_filter_function(False), items)), key=lambda i: i['name'])
        dirs = sorted(list(filter(get_filter_function(True), items)), key=lambda i: i['name'])
        return files, dirs

    def get_image_content(self, filename, key_str):
        request = self.service.files().get_media(fileId=filename)
        fh = BytesIO()
        download = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False
        try:
            while not done:
                status, done = download.next_chunk()
            fh.seek(0)
            with open('temp.enc', 'wb') as f:
                shutil.copyfileobj(fh, f)
            content = fp.decrypt_file('temp.enc', key_str)
            if os.path.exists('temp.enc'):
                os.remove('temp.enc')
            return content
        except Exception as e:
            print(e)
            return None

    def logout(self):
        if os.path.exists('token.json'):
            os.remove('token.json')