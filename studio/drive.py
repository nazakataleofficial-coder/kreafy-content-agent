"""Optional read-only Drive asset import. No connection or sharing is created.

Requires an already-authorized service account and explicit folder ID. This
module never deletes Drive files, changes permissions or publishes media.
"""
import hashlib
import io
import json
import os
import re
from pathlib import Path

MAX_BYTES = 10 * 1024 * 1024


def import_images(folder_id, destination):
    if not re.fullmatch(r'[A-Za-z0-9_-]{10,200}', folder_id):
        raise ValueError('An explicit Drive folder ID is required')
    credential = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '')
    if not credential:
        raise ValueError('Drive not connected; authorize read-only access separately')
    # Lazy imports keep the default offline preparation independent of Drive SDKs.
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(credential), scopes=['https://www.googleapis.com/auth/drive.readonly'])
    service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    items, page = [], None
    while True:
        data = service.files().list(q=f"'{folder_id}' in parents and trashed = false and (mimeType = 'image/png' or mimeType = 'image/jpeg')",
                    pageSize=100, pageToken=page, fields='nextPageToken,files(id,mimeType,size)').execute()
        for item in data.get('files', []):
            if len(items) >= 50:
                raise ValueError('Import limited to 50 images per run; choose a smaller folder')
            if int(item.get('size', MAX_BYTES + 1)) > MAX_BYTES:
                raise ValueError('Drive image exceeds 10 MiB limit')
            buffer = io.BytesIO()
            download = MediaIoBaseDownload(buffer, service.files().get_media(fileId=item['id']), chunksize=1024*1024)
            done = False
            while not done:
                _, done = download.next_chunk(num_retries=0)
                if buffer.tell() > MAX_BYTES:
                    raise ValueError('Drive image exceeded import limit during download')
            blob = buffer.getvalue()
            from PIL import Image
            with Image.open(io.BytesIO(blob)) as photo:
                photo.verify()
            suffix = '.png' if item['mimeType'] == 'image/png' else '.jpg'
            output = destination / (hashlib.sha256(blob).hexdigest() + suffix)
            output.write_bytes(blob)
            items.append(str(output))
        page = data.get('nextPageToken')
        if not page:
            return items
