from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.env import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError, ExpiredSignatureError
from app.models.token import Token
from app.constant import ACCESS_TOKEN


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_token(data: dict, expires_delta: Optional[timedelta] = None, token_type: str = ACCESS_TOKEN):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_token(token: str, db: Session, expected_token: Optional[str] = None):

            if expected_token is not None:
                decode_type = jwt.get_unverified_claims(token).get("type")
                if decode_type != expected_token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token does not match the expected value",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

            revoked = db.query(Token).filter(Token.token == token).first()
            if revoked:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id: str = payload.get("sub")
                if user_id is None:
                    raise credentials_exception()
                return user_id
            except ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except JWTError:
                raise credentials_exception()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = verify_token(token, db, expected_token=ACCESS_TOKEN)
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise credentials_exception()
    # if not user.is_active:
    #     raise HTTPException(status_code=403, detail="Inactive user")
    return user


def revoke_token(token: str, db: Session = Depends(get_db), valid_until: datetime = None):
    revoked_token = Token(token=token, valid_until=valid_until)
    db.add(revoked_token)
    db.commit()

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
