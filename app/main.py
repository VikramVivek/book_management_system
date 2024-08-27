import logging

from fastapi import FastAPI

from app.logging_config import setup_logging

from .config import HOST, LOG_LEVEL, PORT
from .database import init_db
from .routers import admin, auth, books, recommendations, reviews, summarization, users

# Setup logging configuration
setup_logging()
logger = logging.getLogger("app")


def create_app():
    """
    Create and configure the FastAPI application.

    This function initializes the FastAPI application with a title, description,
    and version. It also includes all the routers for different parts of the application
    and sets up the database initialization on startup.

    Returns:
        FastAPI: The configured FastAPI application.
    """
    app = FastAPI(
        title="Book Management System API",
        description=(
            "API for managing books, users, reviews, and recommendations "
            "in the Book Management System"
        ),
        version="1.0.0",
        openapi_tags=[
            {
                "name": "Setup Test Env",
                "description": (
                    "For testing APIs, initial setup of dummy"
                    "data, admin creation and resetting database."
                ),
            },
            {
                "name": "User Management",
                "description": (
                    "Operations related to user registration, "
                    "authentication, and profile management."
                ),
            },
            {
                "name": "Book Management",
                "description": (
                    "Operations for creating, retrieving, updating, "
                    "and deleting books."
                ),
            },
            {
                "name": "Review Management",
                "description": (
                    "Operations for adding, updating, and deleting reviews of books."
                ),
            },
            {
                "name": "Recommendations",
                "description": (
                    "Operations for generating and retrieving book recommendations."
                ),
            },
            {
                "name": "Book Summarization",
                "description": (
                    "Operations related to generating summaries for books."
                ),
            },
            {
                "name": "Admin",
                "description": (
                    "Administrative operations including user and review management."
                ),
            },
        ],
    )

    # Include the routers
    logger.debug("Including routers for various endpoints")
    app.include_router(auth.router, prefix="/auth")
    app.include_router(users.router, prefix="/users")
    app.include_router(admin.router, prefix="/admin")
    app.include_router(books.router, prefix="/books")
    app.include_router(reviews.router, prefix="/reviews")
    app.include_router(recommendations.router, prefix="/recommendations")
    app.include_router(summarization.router, prefix="/summarization")

    @app.on_event("startup")
    def startup_event():
        """
        Event triggered on application startup.

        This function initializes the database connection and logs the startup event.
        """
        logger.info("Application startup event triggered")
        init_db()

    @app.get("/")
    def read_root():
        """
        Root endpoint of the application.

        This endpoint returns a welcome message and logs when it is accessed.

        Returns:
            dict: A welcome message.
        """
        logger.info("Root endpoint accessed")
        return {"message": "Welcome to the Intelligent Book Management System!"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting the application on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, log_level=LOG_LEVEL)
