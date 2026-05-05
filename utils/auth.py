from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from utils.getdb import get_db
from jose import ExpiredSignatureError, jwt
import os
from passlib.context import CryptContext
from typing import Optional, Literal
from utils.authtoken import TokenData
import models
from datetime import datetime, timedelta
from config import settings

import resend
from dotenv import load_dotenv
load_dotenv()
# os.environ["RESEND_API_KEY"]
if not settings.RESEND_API_KEY:
    raise EnvironmentError("RESEND_API_KEY is missing")

resend.api_key = settings.RESEND_API_KEY
# resend = Resend(api_key=resend.api_key)


def send_email(to_email: str, confirmation_link: str):
    try:
        resend.Emails.send(
            {
                "from": "Resend <onboarding@resend.dev>",
                "to": [to_email],
                "subject": "Confirm your email",
                "text": f"Click this link to confirm your account: {confirmation_link}"
            }
        )
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print("Error sending email:", e)


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY = settings.SECRET_KEY
# print("SECRET_KEY:", SECRET_KEY)
ALGORITHM = "HS256"


def create_credentials_exception(detail: str) -> HTTPException:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode = {"sub": email, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_confirmation_token(email: str, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=1440))
    to_encode = {"sub": email, "exp": expire, "type": "confirmation"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(email: str, password: str, db: Session):
    user = get_user_by_email(email, db)
    if not user:
        create_credentials_exception("Invalid email or password")
    if not verify_password(password, user.password_hash):
        create_credentials_exception("Invalid email or password")
    # if not user.confirmed:
      #  raise create_credentials_exception("User has not confirmed email")
    return user


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            create_credentials_exception("Token is missing 'sub' filed")

        token_type = payload.get("type")
        if token_type is None or token_type != "access":
            raise create_credentials_exception(
                f"Token has incorrect type, expected'{token_type}' ")
        return TokenData(email=email)
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Expired",
            headers={"WWW-Authenticate": "Bearer"}
        )from e
    except jwt.JWTError:
        raise create_credentials_exception("Invalid Token ")


def get_user_by_email(email: str, db: Session):
    return db.query(models.User).filter(models.User.email == email).first()


def get_subject_for_token_type(token: str, type: Literal["access", "confirmation"]) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except ExpiredSignatureError as e:
        raise create_credentials_exception("Token Expired") from e
    except jwt.JWTError:
        raise create_credentials_exception("Invalid Token ")

    email: str = payload.get("sub")
    if email is None:
        raise create_credentials_exception("Token is missing 'sub' failed")

    token_type = payload.get("type")
    if token_type is None or token_type != type:
        raise create_credentials_exception(
            f"Token has incorrect type, expected'{token_type}' ")

    return email


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # token_data = verify_token(token)
    # email = get_subject_for_token_type(token, "access")
    # Verify token
    token_data = verify_token(token)
    # Fetch user
    user = db.query(models.User).filter(
        models.User.email == token_data.email).first()
    # email = get_subject_for_token_type(token, "access")
    # Check if email is confirmed
    if not user.confirmed:
        raise create_credentials_exception(
            "could not find user for this token")
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=404,
            detail="Inactive User",
        )
    return current_user
