from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    copies: int = Field(ge=1)

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    copies: Optional[int] = Field(None, ge=1)

class BookAvailabilityUpdate(BaseModel):
    available_copies: int
    operation: str = Field(..., description="Either 'increment' or 'decrement' or 'set'")

class BookInDB(BookBase):
    id: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BookResponse(BookInDB):
    pass

class BookSearchResponse(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    per_page: int
