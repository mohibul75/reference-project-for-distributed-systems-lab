from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.init_db import get_db
from app.schemas.book import BookCreate, BookResponse, BookUpdate, BookAvailabilityUpdate, BookSearchResponse
from app.services.book_service import BookService
from app.exception.http_exception import BookNotFoundException, ISBNAlreadyExistsException, NoAvailableCopiesException, InvalidRequestException, DatabaseException

router = APIRouter()

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    try:
        db_book = BookService.get_book_by_isbn(db, isbn=book_data.isbn)
        if db_book:
            raise ISBNAlreadyExistsException()
        
        return BookService.create_book(db=db, book_data=book_data)
    except ISBNAlreadyExistsException as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")

@router.get("", response_model=BookSearchResponse)
def search_books(
    search: Optional[str] = None, 
    skip: int = Query(0, ge=0), 
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        result = BookService.search_books(db, search=search, skip=skip, limit=limit)
        return result
    except SQLAlchemyError as e:
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    try:
        db_book = BookService.get_book(db, book_id=book_id)
        if db_book is None:
            raise BookNotFoundException()
        return db_book
    except BookNotFoundException as e:
        raise e
    except SQLAlchemyError as e:
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_data: BookUpdate, db: Session = Depends(get_db)):
    try:
        db_book = BookService.get_book(db, book_id=book_id)
        if db_book is None:
            raise BookNotFoundException()
        
        if book_data.isbn and book_data.isbn != db_book.isbn:
            existing_book = BookService.get_book_by_isbn(db, isbn=book_data.isbn)
            if existing_book:
                raise ISBNAlreadyExistsException()
        
        updated_book = BookService.update_book(db=db, book_id=book_id, book_data=book_data)
        return updated_book
    except (BookNotFoundException, ISBNAlreadyExistsException) as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")

@router.patch("/{book_id}/availability", response_model=BookResponse)
def update_book_availability(book_id: int, availability_data: BookAvailabilityUpdate, db: Session = Depends(get_db)):
    try:
        db_book = BookService.get_book(db, book_id=book_id)
        if db_book is None:
            raise BookNotFoundException()
        
        if availability_data.operation not in ["increment", "decrement", "set"]:
            raise InvalidRequestException(detail="Operation must be 'increment', 'decrement', or 'set'")
        
        if availability_data.operation == "decrement" and db_book.available_copies < availability_data.available_copies:
            raise NoAvailableCopiesException(detail="Not enough available copies")
        
        updated_book = BookService.update_book_availability(
            db=db, 
            book_id=book_id, 
            availability_data=availability_data
        )
        return updated_book
    except (BookNotFoundException, NoAvailableCopiesException, InvalidRequestException) as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    try:
        db_book = BookService.get_book(db, book_id=book_id)
        if db_book is None:
            raise BookNotFoundException()
        
        BookService.delete_book(db=db, book_id=book_id)
        return None
    except BookNotFoundException as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")
