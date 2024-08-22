from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from .. import schemas, models, database, auth
#from fastapi import BackgroundTasks

router = APIRouter()

@router.post("/", response_model=schemas.Book, tags=["Book Management"])
def create_book(
    book: schemas.BookCreate,
    #background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),  # Dependency for the DB session
    current_user: schemas.User = Depends(auth.get_current_active_user)  # Dependency for the current user
):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    # Trigger background task for summary generation
    #background_tasks.add_task(AIService().generate_summary_for_book, db_book.id, db)

    return db_book

@router.get("/{book_id}", response_model=schemas.Book, tags=["Book Management"])
def read_book(book_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    result = db.execute(select(models.Book).filter(models.Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.get("/", response_model=list[schemas.Book], tags=["Book Management"])
def find_books(
    genre: str = None,
    author: str = None,
    title: str = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Book)
    if genre:
        query = query.filter(models.Book.genre == genre)
    if author:
        query = query.filter(models.Book.author == author)
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    return query.all()

@router.put("/{book_id}", response_model=schemas.Book, tags=["Book Management", "Admin"])
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(database.get_db),  current_user: schemas.User = Depends(auth.get_current_active_user)):
    result = db.execute(select(models.Book).filter(models.Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{book_id}", response_model=schemas.Book, tags=["Book Management", "Admin"])
def delete_book(book_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    result = db.execute(select(models.Book).filter(models.Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return db_book
