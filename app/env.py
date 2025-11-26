import os

user = "USER"
password = "PA55WORD"
db_name = "KDB"

SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000") #Windows version
# MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000") #Normal
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = False