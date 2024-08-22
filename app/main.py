from dotenv import load_dotenv
from fastapi import FastAPI

from .database import init_db
from .routers import admin, auth, books, recommendations, reviews, summarization, users

load_dotenv()  # Load environment variables from .env


def create_app():
    app = FastAPI()

    app = FastAPI(
        title="Book Management System API",
        description=(
            "API for managing books, users, reviews, and recommendations "
            "in the Book Management System"
        ),
        version="1.0.0",
        openapi_tags=[
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
                    "Operations for adding, updating, and deleting " "reviews of books."
                ),
            },
            {
                "name": "Recommendations",
                "description": (
                    "Operations for generating and retrieving book " "recommendations."
                ),
            },
            {
                "name": "Book Summarization",
                "description": (
                    "Operations related to generating summaries for " "books."
                ),
            },
            {
                "name": "Admin",
                "description": (
                    "Administrative operations including user and " "review management."
                ),
            },
        ],
    )

    # Include the routers
    app.include_router(auth.router, prefix="/auth")
    app.include_router(users.router, prefix="/users")
    app.include_router(admin.router, prefix="/admin")
    app.include_router(books.router, prefix="/books")
    app.include_router(reviews.router, prefix="/reviews")
    app.include_router(recommendations.router, prefix="/recommendations")
    app.include_router(summarization.router, prefix="/summarization")

    @app.on_event("startup")
    def startup_event():
        init_db()

    @app.get("/")
    def read_root():
        return {"message": "Welcome to the Intelligent Book Management System!"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
