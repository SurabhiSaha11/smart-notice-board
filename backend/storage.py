import os
import uuid
from flask import request

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file):
    """Saves the file and returns a URL that can be stored in the database."""
    ext = file.filename.rsplit('.', 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(UPLOAD_FOLDER, name))
    return f"{request.host_url}files/{name}"


def delete_file(url):
    if not url:
        return
    name = os.path.basename(url)
    path = os.path.join(UPLOAD_FOLDER, name)
    if os.path.exists(path):
        os.remove(path)