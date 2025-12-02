# FastAPI Application


To run app locally:
install dependencies:
```bash
pip install "uvicorn[standard]"
```
and after that run:
```bash
uvicorn app.main:app --reload --host 127.0.0.4 --port 8000
```

for debian based systems you can use:
```bash
MINIO_ENDPOINT=localhost:9000 DB_HOST=localhost DB_PORT=15432 uvicorn app.main:app --reload --host 127.0.0.4 --port 8000
```
