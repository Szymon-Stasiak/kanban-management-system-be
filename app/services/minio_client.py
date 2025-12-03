from minio import Minio
import os
from io import BytesIO
from app.env import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE

client = Minio(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)

BUCKET = "mybucket"
endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")

if not client.bucket_exists(bucket_name=BUCKET):
    client.make_bucket(bucket_name=BUCKET)


async def get_file_from_minio(path_in_bucket: str) -> bytes:
    try:
        response = client.get_object(bucket_name=BUCKET, object_name=path_in_bucket)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    except Exception as e:
        raise Exception(f"Error retrieving file from MinIO: {e}")


async def upload_file_to_minio(file, filename: str):
    data = await file.read()
    client.put_object(
        bucket_name=BUCKET,
        object_name=filename,
        data=BytesIO(data),
        length=len(data)
    )
    #todo later change for docker build
    # endpoint = os.getenv("MINIO_ENDPOINT", "minioCloud:9000")
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    return f"http://{endpoint}/{BUCKET}/{filename}"


async def delete_file_from_minio(path_in_bucket: str):
    client.remove_object(bucket_name=BUCKET, object_name=path_in_bucket)


if __name__ == "__main__":
    import asyncio


    async def test_connection():
        try:
            exists = client.bucket_exists(bucket_name=BUCKET)
            print(f"Bucket '{BUCKET}' exists: {exists}")

            print("Files in bucket:")
            for obj in client.list_objects(bucket_name=BUCKET):
                print(f" - {obj.object_name}")

            print("Connection to MinIO works correctly!")
        except Exception as e:
            print("MinIO connection error:", e)


    asyncio.run(test_connection())
