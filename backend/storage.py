import os
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from flask import request

load_dotenv()

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CONN_STR = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER', 'attachments')
USE_AZURE = bool(CONN_STR)

if USE_AZURE:
    from azure.storage.blob import (
        BlobServiceClient, ContentSettings, BlobSasPermissions, generate_blob_sas
    )
    _service = BlobServiceClient.from_connection_string(CONN_STR)
    _container = _service.get_container_client(CONTAINER)
    try:
        _container.create_container()
    except Exception:
        pass  # container already exists


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file):
    """Saves the file. Returns what gets stored in the database."""
    ext = file.filename.rsplit('.', 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"

    if USE_AZURE:
        _container.upload_blob(
            name=name,
            data=file.stream,
            overwrite=True,
            content_settings=ContentSettings(content_type=file.mimetype),
        )
        return name  # only the blob name is stored

    file.save(os.path.join(UPLOAD_FOLDER, name))
    return f"{request.host_url}files/{name}"


def get_url(stored):
    """Turns the stored value into a link the browser can open."""
    if not stored:
        return None
    if not USE_AZURE or stored.startswith('http'):
        return stored  # local file, or an old local record

    sas = generate_blob_sas(
        account_name=_service.account_name,
        container_name=CONTAINER,
        blob_name=stored,
        account_key=_service.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    return f"{_service.get_blob_client(CONTAINER, stored).url}?{sas}"


def delete_file(stored):
    if not stored:
        return
    if USE_AZURE and not stored.startswith('http'):
        try:
            _container.delete_blob(stored)
        except Exception:
            pass
        return

    path = os.path.join(UPLOAD_FOLDER, os.path.basename(stored))
    if os.path.exists(path):
        os.remove(path)