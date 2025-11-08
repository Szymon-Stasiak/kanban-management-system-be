from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db
from app.models.user import User
from app.utils import verify_password, hash_password, generate_token
from app.services.jwt_service import create_token
from app.schemas.user_schema import UserCreate, UserOut
from app.constant import ACTIVE, DELETED

router = APIRouter()


@router.post("/register", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user and db_user.status != DELETED:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    verification_token = generate_token()

    if db_user and db_user.status == DELETED:
        db_user.username = user.username
        db_user.password_hash = hashed_password
        db_user.name = user.name
        db_user.surname = user.surname
        db_user.verification_token = verification_token
        db_user.status = ACTIVE
        db.commit()
        db.refresh(db_user)
        return db_user

    new_user = User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password,
        name=user.name,
        surname=user.surname,
        verification_token=verification_token
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or user.status == DELETED or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token(data={"sub": str(user.user_id)})
    return {"token": access_token, "token_type": "bearer"}
