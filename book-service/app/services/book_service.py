from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, BookAvailabilityUpdate

class BookService:
    @staticmethod
    def create_book(db: Session, book_data: BookCreate) -> Book:
        db_book = Book(
            title=book_data.title,
            author=book_data.author,
            isbn=book_data.isbn,
            copies=book_data.copies,
            available_copies=book_data.copies
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    
    @staticmethod
    def get_book(db: Session, book_id: int) -> Optional[Book]:
        return db.query(Book).filter(Book.id == book_id).first()
    
    @staticmethod
    def get_book_by_isbn(db: Session, isbn: str) -> Optional[Book]:
        return db.query(Book).filter(Book.isbn == isbn).first()
    
    @staticmethod
    def search_books(db: Session, search: str = None, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        query = db.query(Book)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term),
                    Book.isbn.ilike(search_term)
                )
            )
        
        total = query.count()
        books = query.offset(skip).limit(limit).all()
        
        return {
            "books": books,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "per_page": limit
        }
    
    @staticmethod
    def update_book(db: Session, book_id: int, book_data: BookUpdate) -> Optional[Book]:
        db_book = BookService.get_book(db, book_id)
        if not db_book:
            return None
        
        update_data = book_data.model_dump(exclude_unset=True)
        
        if "copies" in update_data:
            new_copies = update_data["copies"]
            difference = new_copies - db_book.copies
            update_data["available_copies"] = max(0, db_book.available_copies + difference)
        
        for key, value in update_data.items():
            setattr(db_book, key, value)
        
        db.commit()
        db.refresh(db_book)
        return db_book
    
    @staticmethod
    def update_book_availability(db: Session, book_id: int, availability_data: BookAvailabilityUpdate) -> Optional[Book]:
        db_book = BookService.get_book(db, book_id)
        if not db_book:
            return None
        
        if availability_data.operation == "increment":
            db_book.available_copies = min(db_book.copies, db_book.available_copies + availability_data.available_copies)
        elif availability_data.operation == "decrement":
            db_book.available_copies = max(0, db_book.available_copies - availability_data.available_copies)
        elif availability_data.operation == "set":
            db_book.available_copies = min(db_book.copies, max(0, availability_data.available_copies))
        
        db.commit()
        db.refresh(db_book)
        return db_book
    
    @staticmethod
    def delete_book(db: Session, book_id: int) -> bool:
        db_book = BookService.get_book(db, book_id)
        if not db_book:
            return False
        
        db.delete(db_book)
        db.commit()
        return True
