from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urlparse
import uuid
from app.db.database import get_db
from app.models.user import User
from app.services.jwt_service import get_current_user
from app.services.minio_client import upload_file_to_minio, delete_file_from_minio, BUCKET , get_file_from_minio
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter()


@router.get("/my-profile-picture")
async def get_profile_picture(
        current_user: User = Depends(get_current_user),
):
    if not current_user.avatar_url:
        raise HTTPException(status_code=404, detail="No profile picture found")

    path_in_bucket = urlparse(current_user.avatar_url).path.lstrip(f"/{BUCKET}/")
    file_data = await get_file_from_minio(path_in_bucket)

    return StreamingResponse(BytesIO(file_data), media_type="application/octet-stream")

@router.post("/upload")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    filename = f"profile_pictures/{current_user.user_id}_{uuid.uuid4()}_{file.filename}"
    url = await upload_file_to_minio(file, filename)
    current_user.avatar_url = url
    db.commit()
    db.refresh(current_user)
    return {"profile_picture_url": url}



@router.put("/edit")
async def edit_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.profile_picture_url:
        path_in_bucket = urlparse(current_user.profile_picture_url).path.lstrip(f"/{BUCKET}/")
        await delete_file_from_minio(path_in_bucket)

    filename = f"/{current_user.user_id}_{uuid.uuid4()}_{file.filename}"
    url = await upload_file_to_minio(file, filename)
    current_user.profile_picture_url = url
    db.commit()
    db.refresh(current_user)
    return {"profile_picture_url": url}


@router.delete("/delete")
async def delete_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.avatar_url:
        raise HTTPException(status_code=404, detail="No profile picture to delete")

    path_in_bucket = urlparse(current_user.avatar_url).path.lstrip(f"/{BUCKET}/")
    await delete_file_from_minio(path_in_bucket)

    current_user.avatar_url = None
    db.commit()
    db.refresh(current_user)
    return {"detail": "Profile picture deleted"}
