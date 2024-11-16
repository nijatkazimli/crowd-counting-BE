from azure.storage.blob import BlobServiceClient, PublicAccess

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
