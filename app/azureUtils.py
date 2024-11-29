from azure.storage.blob import BlobServiceClient, PublicAccess
from urllib.parse import urlparse
import os

def get_blob_service_client(connection_str):
    return BlobServiceClient.from_connection_string(connection_str)

def create_container_if_not_exists(blob_service_client, container_name):
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container(public_access=PublicAccess.Blob)
        print(f"Container '{container_name}' created and set to public access.")
    except Exception as e:
        if "ContainerAlreadyExists" in str(e):
            print(f"Container '{container_name}' already exists.")
        else:
            raise

def upload_file_to_blob(file, container_name, blob_service_client):
    create_container_if_not_exists(blob_service_client, container_name)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)
    blob_client.upload_blob(file, overwrite=True)
    return blob_client.url

def upload_file_path_to_blob(file_path, container_name, blob_service_client):
    create_container_if_not_exists(blob_service_client, container_name)
    file_name = os.path.basename(file_path)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    with open(file_path, "rb") as file:
        blob_client.upload_blob(file, overwrite=True)
    return blob_client.url

def download_file_from_blob(url, blob_service_client, download_path, container_name):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    blob_name = path_parts[-1]  # Last part is the file name
    os.makedirs(download_path, exist_ok=True)
    download_file_path = os.path.join(download_path, blob_name)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    return download_file_path