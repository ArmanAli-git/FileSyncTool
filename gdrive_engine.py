import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io


SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_vip_badge():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


_DRIVE_SERVICE = None


def get_drive_service():
    global _DRIVE_SERVICE
    if not _DRIVE_SERVICE:
        creds = get_vip_badge()
        _DRIVE_SERVICE = build('drive', 'v3', credentials=creds)
    return _DRIVE_SERVICE


def get_or_create_root_folder():
    service = get_drive_service()

    query = "name = 'FileSyncTool_Backup' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
    
    if files:
        return files[0]['id']
    else:
        folder_metadata = {
            'name': 'FileSyncTool_Backup',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')


def get_user_cloud_folders():
    service = get_drive_service()
    
    parent_folder_id = get_or_create_root_folder()
    query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    response = service.files().list(q=query, fields="files(id, name)", pageSize=30).execute()
    
    return response.get('files', [])


def create_sync_folder(folder_name):
    service = get_drive_service()

    parent_folder_id = get_or_create_root_folder()

    folder_metadata = {
        'name': folder_name,
        'parents': [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')


def lock_in_sync_folder(folder_name):
    service = get_drive_service()

    parent_folder_id = get_or_create_root_folder()

    query = f"name = '{folder_name}' and '{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
    
    if files:
        return files[0]['id']
    else:
        folder_metadata = {
            'name': folder_name,
            'parents': [parent_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')



def scan_cloud_folder(folder_id):
    service = get_drive_service()
    
    query = f"'{folder_id}' in parents and trashed = false"
    response = service.files().list(q=query, fields="files(id, name, modifiedTime, size)").execute()
    
    return response.get('files', [])


def upload_file(local_file_path, target_folder_id):
    service = get_drive_service()
    
    file_name = os.path.basename(local_file_path)
    file_metadata = {'name': file_name, 'parents': [target_folder_id]}
    media = MediaFileUpload(local_file_path, resumable=True)
    
    uploaded_file = service.files().create(
        body=file_metadata, 
        media_body=media, 
        fields='id'
    ).execute()
    
    return uploaded_file.get('id')


def download_file(file_id, local_file_path):
    service = get_drive_service()
    
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(local_file_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
    return local_file_path