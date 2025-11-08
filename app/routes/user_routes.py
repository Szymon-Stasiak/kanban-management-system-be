from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Query
from app.db.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserOut, UserUpdate
from app.services.jwt_service import get_current_user , decode_token, revoke_token
from app.constant import DELETED
from fastapi import Request
from app.models.token import Token
from fastapi import Body
from datetime import datetime, timezone

router = APIRouter()

@router.get("/me", response_model=UserOut)
def get_user_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



@router.delete("/deleteme", response_model=UserOut)
def delete_own_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = DELETED
    db.commit()
    db.refresh(user)

    token_str = get_authorization_header(request)
    valid_until_ts = decode_token(token_str).get("exp") if token_str else None
    if token_str and valid_until_ts:
        valid_until_dt = datetime.fromtimestamp(valid_until_ts, tz=timezone.utc)
        revoke_token(token=token_str, db=db, valid_until=valid_until_dt)

    return user


def get_authorization_header(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

@router.put("/edit", response_model=UserOut)
def update_own_account(
    user_update: UserUpdate = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.surname is not None:
        user.surname = user_update.surname
    if user_update.bio is not None:
        user.bio = user_update.bio
    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url

    db.commit()
    db.refresh(user)

    return user
