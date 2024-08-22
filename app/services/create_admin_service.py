from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.database import get_db
from app.models import User


def create_admin(
    email: str = "admin@example.com",
    username: str = "admin",
    password: str = "adminpassword",
    db: Session = Depends(get_db),
):
    # Check if the admin already exists
    existing_admin = db.query(User).filter(User.email == email).first()
    if existing_admin:
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

    return {"detail": "Admin user created successfully", "user": admin_user.username}
