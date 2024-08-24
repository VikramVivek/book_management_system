from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True
        from_attributes = True


class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    year_of_publication: int
    content: str


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class Book(BookBase):
    id: int
    summary: str
    reviews: List["Review"] = []

    class Config:
        orm_mode = True
        from_attributes = True


class ReviewBase(BaseModel):
    review_text: str
    rating: int


class ReviewCreate(ReviewBase):
    pass


class Review(ReviewBase):
    id: int
    book_id: int
    user_id: int

    class Config:
        orm_mode = True


class OAuth2PasswordRequestFormCustom:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
    ):
        self.username = username
        self.password = password


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserPreferencesBase(BaseModel):
    preferred_genres: str
    preferred_authors: str


class UserPreferencesCreate(UserPreferencesBase):
    pass


class UserPreferences(UserPreferencesBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
        from_attributes = True


class RecommendationBase(BaseModel):
    recommended_books: List[int]  # List of book IDs


class RecommendationCreate(RecommendationBase):
    pass


class Recommendation(RecommendationBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
