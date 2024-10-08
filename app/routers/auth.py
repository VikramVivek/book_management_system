import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, database, models, schemas
from ..auth import create_access_token, get_password_hash

# Setup logger
logger = logging.getLogger("app.auth")

router = APIRouter()


@router.post("/register", response_model=schemas.User, tags=["User Management"])
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    Register a new user.

    Args:
        user (schemas.UserCreate): The user registration details.
        db (Session): The database session.

    Returns:
        schemas.User: The newly created user.
    """
    logger.info("Attempting to register a new user.")
    db_user = (
        db.query(models.User)
        .filter(
            (models.User.email == user.email) | (models.User.username == user.username)
        )
        .first()
    )
    if db_user:
        logger.warning("Registration failed: Email or Username already registered.")
        raise HTTPException(
            status_code=400, detail="Email or Username already registered"
        )

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role="user",
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User {db_user.username} registered successfully.")
    return db_user


@router.post("/token", response_model=schemas.Token, tags=["User Management"])
def login_for_access_token(
    form_data: schemas.OAuth2PasswordRequestFormCustom = Depends(),
    db: Session = Depends(database.get_db),
):
    """
    Authenticate the user and return an access token.

    Args:
        form_data (schemas.OAuth2PasswordRequestFormCustom): The user login details.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the access token and token type.
    """
    logger.info(f"Attempting to authenticate user {form_data.username}.")
    user = (
        db.query(models.User).filter(models.User.email == form_data.username).first()
    )  # Authenticate with email
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        logger.warning("Authentication failed: Incorrect email or password.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )

    logger.info(f"User {form_data.username} authenticated successfully.")
    return {"access_token": access_token, "token_type": "bearer"}
