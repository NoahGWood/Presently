from google.cloud import storage

BUCKET_ID = os.environ.get("BUCKET_ID", 'presently')

client = storage.Client()

BUCKET = client.get_bucket(BUCKET_ID)

def load_file_bytes(remote):
    blob = BUCKET.get_blob(remote)
    return blob.download_as_bytes()

def load_file_locally(remote, local):
    blob = BUCKET.get_blob(remote)
    return blob.download_to_filename(local)

def load_file_text(remote):
    blob = BUCKET.get_blob(remote)
    return blob.download_as_text()

def upload_file_from_local(remote, fname):
    """Uploads (or updates) the bucket with from a locally saved file."""
    blob = BUCKET.get_blob(remote)
    blob.upload_from_filename(fname)

def upload_file_from_txt(remote, txt):
    """Uploads (or updates) the bucket with text."""
    blob = BUCKET.get_blob(remote)
    blob.upload_from_text(txt)

