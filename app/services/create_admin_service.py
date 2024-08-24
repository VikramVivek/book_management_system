import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.database import get_db
from app.models import User

# Setup logger
logger = logging.getLogger("app.create_admin_service")


def create_admin(
    email: str = "admin@example.com",
    username: str = "admin",
    password: str = "adminpassword",
    db: Session = Depends(get_db),
):
    """
    Create an admin user if one does not already exist.

    Args:
        email (str): Default 'admin@example.com'.
        username (str): Default 'admin'.
        password (str): Default 'adminpassword'.
        db (Session): Database session dependency.

    Returns:
        dict: A dictionary containing the success message and
              the username of the created admin user.

    Raises:
        HTTPException: If an admin user with the provided email already exists.
    """
    logger.info("Attempting to create admin user.")

    # Check if the admin already exists
    existing_admin = db.query(User).filter(User.email == email).first()
    if existing_admin:
        logger.warning("Admin user already exists with email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user already exists"
        )

    # Create the admin user
    admin_user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        role="admin",  # Ensure that role is set to 'admin'
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    logger.info("Admin user created successfully with username: %s", username)
    return {"detail": "Admin user created successfully", "user": admin_user.username}
