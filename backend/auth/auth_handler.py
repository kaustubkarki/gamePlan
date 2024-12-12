import jwt
from fastapi import Depends, HTTPException, status, APIRouter
#Depends, HTTPException, status, APIRouter: FastAPI classes and functions used for routing, dependency injection, and raising HTTP errors

from fastapi.security import OAuth2PasswordBearer
# A FastAPI utility for extracting the token from a request.

from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
#CryptContext: A class from the passlib library for hashing and verifying passwords.

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import TokenData
from ..models import User

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818159b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
#JWT algorithm choice 
ACCESS_TOKEN_EXPIRE_MINUTES = 120

#The CryptContext object is configured to use the bcrypt hashing algorithm for password management.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    db_user = db.query(User).filter(User.username == username).first()
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    #A copy of the input data dictionary is created to ensure that the original data is not modified. The function will modify the copied dictionary by adding the expiration time.
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


#get_current_user: This is a dependency function that decodes the JWT token and retrieves the current user from the database.
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    #DRY function
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        # In the context of JWT (JSON Web Tokens), a payload refers to the part of the token that contains the actual data being transmitted. It is the second section of the JWT, coming after the header and before the signature. The payload contains the claims or information that is being conveyed from the sender to the receiver.
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user
