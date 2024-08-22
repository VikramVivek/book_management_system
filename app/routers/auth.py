from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import schemas, models, database, auth
from ..auth import get_user, get_password_hash, create_access_token, authenticate_user, get_current_user
from typing import List

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/register", response_model=schemas.User, tags=["User Management"])
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter((models.User.email == user.email) | (models.User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email or Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password, role="user")
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=schemas.Token, tags=["User Management"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()  # Authenticate with email
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email,"role": user.role}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

