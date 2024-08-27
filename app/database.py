import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL
from .models import Base

# Setup logger
logger = logging.getLogger("app.database")

# Create the SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables defined in the models.

    This function is typically called during the application startup.
    """
    logger.info("Initializing the database")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def reset_db():
    """
    Reset the database by dropping all tables and recreating them.

    This function is for development purposes to reset the state of the database.
    """
    logger.warning("Resetting the database - all data will be lost")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database reset and initialized successfully")


def get_db():
    """
    Get a database session that can be used for executing queries.

    This function is typically used in FastAPI dependency injection to provide
    a database session for request handlers.

    Yields:
        db: SQLAlchemy session object.
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")
