from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """
    Base schema for User, containing common fields.
    """

    email: EmailStr
    username: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for creating a new user, extending UserBase with a password field.
    """

    password: str


class User(UserBase):
    """
    Schema representing a user, extending UserBase with id and role.
    """

    id: int
    role: str

    class Config:
        orm_mode = True
        from_attributes = True


class BookBase(BaseModel):
    """
    Base schema for Book, containing common fields.
    """

    title: str
    author: str
    genre: str
    year_of_publication: int
    content: str


class BookCreate(BookBase):
    """
    Schema for creating a new book, extending BookBase.
    """

    pass


class BookUpdate(BookBase):
    """
    Schema for updating an existing book, extending BookBase.
    """

    pass


class Book(BookBase):
    """
    Schema representing a book, extending BookBase with id and summary.
    Includes a list of reviews.
    """

    id: int
    summary: str
    reviews: List["Review"] = []

    class Config:
        orm_mode = True
        from_attributes = True


class ReviewBase(BaseModel):
    """
    Base schema for Review, containing common fields.
    """

    review_text: str
    rating: int


class ReviewCreate(ReviewBase):
    """
    Schema for creating a new review, extending ReviewBase.
    """

    pass


class Review(ReviewBase):
    """
    Schema representing a review, extending ReviewBase with id, book_id, and
    user_id.
    """

    id: int
    book_id: int
    user_id: int

    class Config:
        orm_mode = True


class OAuth2PasswordRequestFormCustom:
    """
    Custom form data schema for handling OAuth2 password request.
    """

    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
    ):
        self.username = username
        self.password = password


class Token(BaseModel):
    """
    Schema representing a JWT token with an access_token and token_type.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema representing token data, primarily the username.
    """

    username: Optional[str] = None


class UserPreferencesBase(BaseModel):
    """
    Base schema for UserPreferences, containing common fields.
    """

    preferred_genres: str
    preferred_authors: str


class UserPreferencesCreate(UserPreferencesBase):
    """
    Schema for creating user preferences, extending UserPreferencesBase.
    """

    pass


class UserPreferences(UserPreferencesBase):
    """
    Schema representing user preferences, extending UserPreferencesBase with id
    and user_id.
    """

    id: int
    user_id: int

    class Config:
        orm_mode = True
        from_attributes = True


class RecommendationBase(BaseModel):
    """
    Base schema for Recommendation, containing a list of recommended book IDs.
    """

    recommended_books: List[int]  # List of book IDs


class RecommendationCreate(RecommendationBase):
    """
    Schema for creating a recommendation, extending RecommendationBase.
    """

    pass


class Recommendation(RecommendationBase):
    """
    Schema representing a recommendation, extending RecommendationBase with id
    and user_id.
    """

    id: int
    user_id: int

    class Config:
        orm_mode = True
