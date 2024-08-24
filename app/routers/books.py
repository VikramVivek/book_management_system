import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from .. import auth, database, models, schemas
from ..services.summarization_service import generate_summary_for_content

# Setup logger
logger = logging.getLogger("app.books")

router = APIRouter()


@router.post("/", response_model=schemas.Book, tags=["Book Management"])
def create_book(
    book: schemas.BookCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Create a new book entry in the database and trigger background task for
    generating summary.

    Args:
        book (schemas.BookCreate): Book details to be created.
        background_tasks (BackgroundTasks): To handle asynchronous tasks.
        db (Session): Database session dependency.
        current_user (schemas.User): The currently authenticated user.

    Returns:
        schemas.Book: The newly created book.
    """
    logger.info(f"Creating book: {book.title} by {book.author}")
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    # Trigger background task for summary generation
    background_tasks.add_task(generate_summary_for_content_task, db_book.id, db)
    logger.info(f"Book created successfully with ID: {db_book.id}")

    return db_book


async def generate_summary_for_content_task(book_id: int, db: Session):
    """
    Background task to generate summary for the book content.

    Args:
        book_id (int): The ID of the book to generate the summary for.
        db (Session): Database session dependency.
    """
    logger.info(f"Generating summary for book ID: {book_id}")
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book:
        summary = await generate_summary_for_content(book.content)
        book.summary = summary
        db.commit()
        logger.info(f"Summary generated and updated for book ID: {book_id}")


@router.get("/{book_id}", response_model=schemas.Book, tags=["Book Management"])
def read_book(
    book_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
):
    """
    Retrieve a book by its ID.

    Args:
        book_id (int): The ID of the book to retrieve.
        db (Session): Database session dependency.
        current_user (schemas.User): The currently authenticated user.

    Returns:
        schemas.Book: The requested book.
    """
    logger.info(f"Fetching book with ID: {book_id}")
    result = db.execute(select(models.Book).filter(models.Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        logger.warning(f"Book with ID: {book_id} not found")
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.get("/", response_model=list[schemas.Book], tags=["Book Management"])
def find_books(
    genre: str = None,
    author: str = None,
    title: str = None,
    db: Session = Depends(database.get_db),
):
    """
    Find books based on genre, author, or title.

    Args:
        genre (str, optional): Filter books by genre.
        author (str, optional): Filter books by author.
        title (str, optional): Filter books by title.
        db (Session): Database session dependency.

    Returns:
        list[schemas.Book]: A list of books matching the filters.
    """
    logger.info(
        f"Searching for books with filters - Genre: {genre}, Author: {author},",
        f" Title: {title}",
    )
    query = db.query(models.Book)
    if genre:
        query = query.filter(models.Book.genre == genre)
    if author:
        query = query.filter(models.Book.author == author)
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    return query.all()


@router.patch(
    "/{book_id}", response_model=schemas.Book, tags=["Book Management", "Admin"]
)
def update_book(
    book_id: int,
    book: schemas.BookCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Update the details of an existing book.

    Args:
        book_id (int): The ID of the book to update.
        book (schemas.BookCreate): The new book details.
        db (Session): Database session dependency.
        current_user (schemas.User): The currently authenticated user.

    Returns:
        schemas.Book: The updated book.
    """
    logger.info(f"Updating book with ID: {book_id}")
    result = db.execute(select(models.Book).filter(models.Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        logger.warning(f"Book with ID: {book_id} not found")
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book.dict(exclude_unset=True)  # Only update fields that are set
    for key, value in update_data.items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)
    logger.info(f"Book with ID: {book_id} updated successfully")
    return db_book


@router.delete(
    "/{book_id}", response_model=schemas.Book, tags=["Book Management", "Admin"]
)
def delete_book(
    book_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Delete a book by its ID.

    Args:
        book_id (int): The ID of the book to delete.
        db (Session): Database session dependency.
        current_user (schemas.User): The currently authenticated user.

    Returns:
        schemas.Book: The deleted book.
    """
    logger.info(f"Deleting book with ID: {book_id}")
    result = db.execute(select(models.Book).filter(models.Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        logger.warning(f"Book with ID: {book_id} not found")
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    logger.info(f"Book with ID: {book_id} deleted successfully")
    return db_book
