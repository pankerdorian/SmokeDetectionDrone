from firebase_admin import credentials, initialize_app, storage

# Init firebase with credentials
cred = credentials.Certificate('firedetectiondrone-9b202-738c5aa6b297.json')  # DOWNLOADED CREDENTIALS FILE (JSON)
initialize_app(cred, {'storageBucket': 'firedetectiondrone-9b202.appspot.com'})  # FIREBASE STORAGE PATH (without gs://)

def add_to_storage(file_name):
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    blob.make_public()
    return blob.public_url
