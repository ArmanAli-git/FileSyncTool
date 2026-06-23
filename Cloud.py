import io
import os.path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class Engine:
    def __init__(self):
        self.service = None
        self.root_id = None
        self.target_id = None

    def authenticate(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        self.service = build("drive", "v3", credentials=creds)
        return "Authenticated"

    def get_create_root(self):
        query = "name = 'FileSyncTool_Root' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        response = (
            self.service.files().list(q=query, fields="files(id, name)").execute()
        )
        files = response.get("files", [])

        if files:
            self.root_id = files[0]["id"]
        else:
            metadata = {
                "name": "FileSyncTool_Root",
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = self.service.files().create(body=metadata, fields="id").execute()
            self.root_id = folder.get("id")

        return self.root_id

    def scan_root(self):
        query = f"'{self.root_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        response = (
            self.service.files()
            .list(q=query, fields="files(id, name)", pageSize=50)
            .execute()
        )
        return response.get("files", [])

    def create_folder(self, folder_name):
        metadata = {
            "name": folder_name,
            "parents": [self.root_id],
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = self.service.files().create(body=metadata, fields="id").execute()
        return folder.get("id")

    def get_create_path(self, relative_path, base_folder_id=None):
        parent_id = base_folder_id or self.root_id
        if not relative_path or relative_path in [".", "/", "\\"]:
            return parent_id

        parts = relative_path.replace("\\", "/").strip("/").split("/")

        for part in parts:
            query = f"'{parent_id}' in parents and name = '{part}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            response = (
                self.service.files().list(q=query, fields="files(id, name)").execute()
            )
            files = response.get("files", [])

            if files:
                parent_id = files[0]["id"]
            else:
                metadata = {
                    "name": part,
                    "parents": [parent_id],
                    "mimeType": "application/vnd.google-apps.folder",
                }
                folder = (
                    self.service.files().create(body=metadata, fields="id").execute()
                )
                parent_id = folder.get("id")

        return parent_id

    def select_folder(self, folder_id):
        self.target_id = folder_id
        return self.target_id

    def scan_selected_folder(self, folder_id, current_path=""):
        query = f"'{folder_id}' in parents and trashed = false"

        page_token = None

        while True:
            response = (
                self.service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
                    pageToken=page_token,
                    pageSize=100,
                )
                .execute()
            )

            items = response.get("files", [])

            for item in items:
                item_path = (
                    f"{current_path}/{item['name']}" if current_path else item["name"]
                )
                is_folder = item["mimeType"] == "application/vnd.google-apps.folder"

                yield {
                    "id": item["id"],
                    "name": item["name"],
                    "path": item_path,
                    "is_dir": is_folder,
                    "modified": item.get("modifiedTime"),
                }

                if is_folder:
                    yield from self.scan_selected_folder(
                        item["id"], current_path=item_path
                    )

            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    def upload_files(self, local_file_path, parent_id=None):
        target_folder = parent_id or self.target_id
        file_name = os.path.basename(local_file_path)
        metadata = {"name": file_name, "parents": [target_folder]}
        media = MediaFileUpload(local_file_path, resumable=True)

        uploaded_file = (
            self.service.files()
            .create(body=metadata, media_body=media, fields="id")
            .execute()
        )
        return uploaded_file.get("id")

    def download_files(self, file_id, local_file_path):
        request = self.service.files().get_media(fileId=file_id)
        with io.FileIO(local_file_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        return local_file_path

    def delete_files(self, file_id):
        self.service.files().delete(fileId=file_id).execute()
