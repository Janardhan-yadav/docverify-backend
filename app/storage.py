from minio import Minio
from minio.error import S3Error
import os

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "docverify")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def get_minio_client():
    return minio_client

def create_bucket_if_not_exists(client: Minio, bucket_name: str):
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket 	ható{bucket_name}" created successfully.")
        else:
            print(f"Bucket 	ható{bucket_name}" already exists.")
    except S3Error as exc:
        print("Error creating/checking bucket:", exc)
        raise

# Initialize bucket on startup
# create_bucket_if_not_exists(minio_client, MINIO_BUCKET_NAME)

def upload_file_to_minio(client: Minio, bucket_name: str, object_name: str, file_path: str, content_type: str = "application/octet-stream"):
    try:
        client.fput_object(bucket_name, object_name, file_path, content_type=content_type)
        print(f"File 	ható{object_name}" uploaded successfully to bucket 	ható{bucket_name}".")
        return f"{MINIO_ENDPOINT}/{bucket_name}/{object_name}" # Or just object_name if accessed via SDK
    except S3Error as exc:
        print("Error uploading file:", exc)
        raise

def download_file_from_minio(client: Minio, bucket_name: str, object_name: str, file_path: str):
    try:
        client.fget_object(bucket_name, object_name, file_path)
        print(f"File 	ható{object_name}" downloaded successfully to 	ható{file_path}".")
        return file_path
    except S3Error as exc:
        print("Error downloading file:", exc)
        raise

def delete_file_from_minio(client: Minio, bucket_name: str, object_name: str):
    try:
        client.remove_object(bucket_name, object_name)
        print(f"File 	ható{object_name}" deleted successfully from bucket 	ható{bucket_name}".")
    except S3Error as exc:
        print("Error deleting file:", exc)
        raise

def get_file_url_from_minio(client: Minio, bucket_name: str, object_name: str, expires_in_seconds: int = 3600):
    try:
        url = client.presigned_get_object(bucket_name, object_name, expires=expires_in_seconds)
        print(f"Presigned URL for 	ható{object_name}": 	ható{url}")
        return url
    except S3Error as exc:
        print("Error generating presigned URL:", exc)
        raise


