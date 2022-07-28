import os
from google.cloud import storage

# Check if we're local
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None) == None:
    # Non local, manually load credentials
    a = os.environ.get("GOOGLE_CREDENTIALS")
    a = a.replace("'", '"')
    with open("creds.json", 'w') as f:
        f.write(a)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="creds.json"

client = storage.Client()

BUCKET_ID = os.environ.get("BUCKET_ID", 'presently')


BUCKET = client.get_bucket(BUCKET_ID)


def load_file_bytes(remote):
    blob = BUCKET.blob(remote)
    return blob.download_as_bytes()

def load_file_locally(remote, local):
    blob = BUCKET.blob(remote)
    return blob.download_to_filename(local)

def load_file_text(remote):
    blob = BUCKET.blob(remote)
    x = blob.download_as_string()
    return x.decode("utf-8") 

def upload_file_from_local(remote, fname):
    """Uploads (or updates) the bucket with from a locally saved file."""
    blob = BUCKET.blob(remote)
    blob.upload_from_filename(fname)

def upload_file_from_txt(remote, txt):
    """Uploads (or updates) the bucket with text."""
    blob = BUCKET.blob(remote)
    print(blob)
    blob.upload_from_string(txt)

