import bcrypt
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from .models import User
from .database import get_db
from .upload import save_file

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True


def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


@router.post("/signup")
def signup(user: UserCreate, avatar: UploadFile = File(None), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hash_password(user.password)
    db_user = User(email=user.email, password_hash=password_hash)

    if avatar:
        filename = f"{user.email}_avatar.jpg"
        avatar_path = save_file(avatar, filename)
        db_user.avatar_path = avatar_path

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "User created successfully", "avatar_path": db_user.avatar_path}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email}


@router.post("/upload-avatar")
async def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_folder = "./uploaded_avatars"
    os.makedirs(upload_folder, exist_ok=True)
    file_location = os.path.join(upload_folder, file.filename)

    with open(file_location, "wb") as f:
        f.write(await file.read())

    current_user_email = get_current_user()
    user = db.query(User).filter(User.email == current_user_email).first()

    user.avatar_url = file_location
    db.commit()
    db.refresh(user)

    return {"msg": "Avatar uploaded successfully", "file_location": file_location}