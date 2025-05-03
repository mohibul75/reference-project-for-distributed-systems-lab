from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.loan import Loan
from app.schemas.loan import LoanCreate, UserBase, BookBase
from app.services.external_service import ExternalServiceClient
from app.exception.http_exception import NoAvailableCopiesException, InvalidRequestException

class LoanService:
    @staticmethod
    async def create_loan(db: Session, loan_data: LoanCreate) -> Loan:
        book = await ExternalServiceClient.get_book(loan_data.book_id)
        
        if book["available_copies"] <= 0:
            raise NoAvailableCopiesException()
        
        await ExternalServiceClient.update_book_availability(
            book_id=loan_data.book_id,
            operation="decrement",
            copies=1
        )
        
        db_loan = Loan(
            user_id=loan_data.user_id,
            book_id=loan_data.book_id,
            due_date=loan_data.due_date,
            status="ACTIVE"
        )
        
        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        return db_loan
    
    @staticmethod
    async def return_book(db: Session, loan_id: int) -> Optional[Loan]:
        db_loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not db_loan:
            return None
        
        if db_loan.status != "ACTIVE":
            raise InvalidRequestException("This loan is not active")
        
        db_loan.status = "RETURNED"
        db_loan.return_date = datetime.now()
        
        await ExternalServiceClient.update_book_availability(
            book_id=db_loan.book_id,
            operation="increment",
            copies=1
        )
        
        db.commit()
        db.refresh(db_loan)
        return db_loan
    
    @staticmethod
    def get_loan(db: Session, loan_id: int) -> Optional[Loan]:
        return db.query(Loan).filter(Loan.id == loan_id).first()
    
    @staticmethod
    def get_user_loans(db: Session, user_id: int) -> Dict[str, Any]:
        loans = db.query(Loan).filter(Loan.user_id == user_id).all()
        return {
            "loans": loans,
            "total": len(loans)
        }
    
    @staticmethod
    async def get_loan_with_details(db: Session, loan_id: int) -> Dict[str, Any]:
        db_loan = LoanService.get_loan(db, loan_id)
        if not db_loan:
            return None
        
        user = await ExternalServiceClient.get_user(db_loan.user_id)
        user_data = UserBase(
            id=user["id"],
            name=user["name"],
            email=user["email"]
        )
        
        book = await ExternalServiceClient.get_book(db_loan.book_id)
        book_data = BookBase(
            id=book["id"],
            title=book["title"],
            author=book["author"]
        )
        
        return {
            "id": db_loan.id,
            "user": user_data,
            "book": book_data,
            "issue_date": db_loan.issue_date,
            "due_date": db_loan.due_date,
            "return_date": db_loan.return_date,
            "status": db_loan.status
        }
    
    @staticmethod
    async def get_user_loans_with_details(db: Session, user_id: int) -> Dict[str, Any]:
        loans = db.query(Loan).filter(Loan.user_id == user_id).all()
        
        result_loans = []
        for loan in loans:
            book = await ExternalServiceClient.get_book(loan.book_id)
            book_data = BookBase(
                id=book["id"],
                title=book["title"],
                author=book["author"]
            )
            
            result_loans.append({
                "id": loan.id,
                "book": book_data,
                "issue_date": loan.issue_date,
                "due_date": loan.due_date,
                "return_date": loan.return_date,
                "status": loan.status
            })
        
        return {
            "loans": result_loans,
            "total": len(result_loans)
        }
