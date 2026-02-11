from azure.storage.blob import BlobServiceClient
from config.settings import AZURE_STORAGE_CONNECTION_STRING, BLOB_CONTAINER_NAME

blob_service = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)

def list_cv_files():
    container = blob_service.get_container_client(BLOB_CONTAINER_NAME)
    return [b.name for b in container.list_blobs()]

def download_cv(file_name: str) -> bytes:
    container = blob_service.get_container_client(BLOB_CONTAINER_NAME)
    blob = container.get_blob_client(file_name)
    return blob.download_blob().readall()
