from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.init_db import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.exception.http_exception import UserNotFoundException, EmailAlreadyExistsException, DatabaseException

router = APIRouter()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = UserService.get_user_by_email(db, email=user_data.email)
        if db_user:
            raise EmailAlreadyExistsException()
        
        return UserService.create_user(db=db, user_data=user_data)
    except EmailAlreadyExistsException as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = UserService.get_user(db, user_id=user_id)
        if db_user is None:
            raise UserNotFoundException()
        return db_user
    except UserNotFoundException as e:
        raise e
    except SQLAlchemyError as e:
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    try:
        db_user = UserService.get_user(db, user_id=user_id)
        if db_user is None:
            raise UserNotFoundException()
        
        if user_data.email and user_data.email != db_user.email:
            existing_user = UserService.get_user_by_email(db, email=user_data.email)
            if existing_user:
                raise EmailAlreadyExistsException()
        
        updated_user = UserService.update_user(db=db, user_id=user_id, user_data=user_data)
        return updated_user
    except (UserNotFoundException, EmailAlreadyExistsException) as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = UserService.get_users(db, skip=skip, limit=limit)
        return users
    except SQLAlchemyError as e:
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
