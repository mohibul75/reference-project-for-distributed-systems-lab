from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.init_db import get_db
from app.schemas.loan import LoanCreate, LoanResponse, ReturnCreate, LoanDetailResponse, UserLoansResponse
from app.services.loan_service import LoanService
from app.exception.http_exception import (
    LoanNotFoundException, UserNotFoundException, BookNotFoundException, 
    NoAvailableCopiesException, ServiceUnavailableException, 
    InvalidRequestException, DatabaseException
)

router = APIRouter()

@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(loan_data: LoanCreate, db: Session = Depends(get_db)):
    try:
        loan = await LoanService.create_loan(db=db, loan_data=loan_data)
        return loan
    except (UserNotFoundException, BookNotFoundException, NoAvailableCopiesException, ServiceUnavailableException) as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")

@router.post("/returns", response_model=LoanResponse)
async def return_book(return_data: ReturnCreate, db: Session = Depends(get_db)):
    try:
        loan = await LoanService.return_book(db=db, loan_id=return_data.loan_id)
        if loan is None:
            raise LoanNotFoundException()
        return loan
    except (LoanNotFoundException, ServiceUnavailableException, InvalidRequestException) as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")

@router.get("/user/{user_id}", response_model=UserLoansResponse)
async def get_user_loans(user_id: int, db: Session = Depends(get_db)):
    try:
        await LoanService.get_user_loans_with_details(db=db, user_id=user_id)
        return await LoanService.get_user_loans_with_details(db=db, user_id=user_id)
    except UserNotFoundException as e:
        raise e
    except ServiceUnavailableException as e:
        raise e
    except SQLAlchemyError as e:
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{loan_id}", response_model=LoanDetailResponse)
async def get_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        loan = await LoanService.get_loan_with_details(db=db, loan_id=loan_id)
        if loan is None:
            raise LoanNotFoundException()
        return loan
    except (LoanNotFoundException, UserNotFoundException, BookNotFoundException, ServiceUnavailableException) as e:
        raise e
    except SQLAlchemyError as e:
        raise DatabaseException(detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        raise InvalidRequestException(detail=f"An unexpected error occurred: {str(e)}")
