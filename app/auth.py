import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import database, models, schemas
from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

# Setup logger
logger = logging.getLogger("app.auth")

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches the hashed password.

    Args:
        plain_password (str): The plain text password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    logger.debug("Verifying password")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    logger.debug("Hashing password")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): The data to include in the token payload.
        expires_delta (Optional[timedelta], optional): The token's time to live.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access token created with expiration at {expire}")
    return encoded_jwt


def get_user(db: Session, username: str) -> Optional[models.User]:
    """
    Retrieve a user by their username or email.

    Args:
        db (Session): The database session.
        username (str): The username or email of the user.

    Returns:
        Optional[models.User]: The user object, if found.
    """
    logger.debug(f"Fetching user with username or email: {username}")
    return (
        db.query(models.User)
        .filter((models.User.email == username) | (models.User.username == username))
        .first()
    )


def authenticate_user(
    db: Session, username: str, password: str
) -> Optional[models.User]:
    """
    Authenticate a user by verifying their password.

    Args:
        db (Session): The database session.
        username (str): The username or email of the user.
        password (str): The plain text password provided by the user.

    Returns:
        Optional[models.User]: The authenticated user object, if successful.
    """
    logger.debug(f"Authenticating user: {username}")
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Authentication failed for user: %s", username)
        return None
    logger.info("User authenticated successfully: %s", username)
    return user


def get_current_user(
    db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)
) -> schemas.User:
    """
    Retrieve the current authenticated user from the token.

    Args:
        db (Session): The database session.
        token (str): The JWT token from the request.

    Returns:
        schemas.User: The current authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get(
            "sub"
        )  # Extracting the subject (username/email) from token
        if username is None:
            logger.error("Token validation failed: username missing in token payload")
            raise credentials_exception
    except JWTError as e:
        logger.error("JWTError: %s", e)
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        logger.warning("User not found for token: %s", username)
        raise credentials_exception
    logger.info("Current user retrieved: %s", username)
    return schemas.User.from_orm(user)  # Return a Pydantic model instance


def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """
    Retrieve the current active user, ensuring they have admin privileges.

    Args:
        current_user (schemas.User): The current authenticated user.

    Returns:
        schemas.User: The current active user if they have admin privileges.

    Raises:
        HTTPException: If the user does not have admin privileges.
    """
    if current_user.role != "admin":
        logger.warning(
            "User %s attempted to access admin resource without sufficient permissions",
            current_user.username,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    logger.info("Admin access granted to user: %s", current_user.username)
    return current_user
