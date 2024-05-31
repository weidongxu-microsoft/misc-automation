import os
from azure.storage.blob import BlobServiceClient

version = "1.7.12"
filename_pattern = f"fluent/runtimev1/{version}/client-runtime-"

connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = service_client.get_container_client("drops")

blob_list = container_client.list_blobs(name_starts_with=filename_pattern)
for blob in blob_list:
    print(f"Downloading blob {blob.name}")
    downloader = container_client.download_blob(blob, validate_content=True)
    data = downloader.readall()

    new_name = blob.name.replace(f"/{version}/", f"/{version}-Rest/")

    print(f"Uploading blob {new_name}")
    container_client.upload_blob(new_name, data, overwrite=False)

    print(f"Deleting blob {blob.name}")
    container_client.delete_blob(blob)
