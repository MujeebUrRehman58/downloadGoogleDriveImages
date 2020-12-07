from __future__ import print_function

import io
import pickle
from os import path
from os import makedirs

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
PATH = path.dirname(__file__)


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists(f'{PATH}/token.pickle'):
        with open(f'{PATH}/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f'{PATH}/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f'{PATH}/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    drive_service = build('drive', 'v3', credentials=creds)

    page_token = None
    makedirs(f'{PATH}/downloads/', exist_ok=True)
    keywords = []
    with open(f'{PATH}/keywords.txt') as file:
        for line in file:
            keywords.append(f"name contains '{line.strip()}'")
    keywords = ' or '.join(keywords)
    while True:
        response = drive_service.files().list(q="mimeType='image/png'"
                                                f"and ({keywords})",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            file_name = file.get('name', '').translate({ord(c): " " for c in "!@#$%^&*()[]{};:,/<>?\|`~=+"})
            file_id = file.get('id')
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.FileIO(f"{PATH}/downloads/{file_name}", 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            print(f"Downloading {file_name}")
            while done is False:
                status, done = downloader.next_chunk()
                print("Progress %d%%" % int(status.progress() * 100))

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break


if __name__ == '__main__':
    main()
