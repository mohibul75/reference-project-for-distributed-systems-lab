from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    id: int
    name: str
    email: str

class BookBase(BaseModel):
    id: int
    title: str
    author: str

class LoanBase(BaseModel):
    user_id: int
    book_id: int
    due_date: datetime

class LoanCreate(LoanBase):
    pass

class ReturnCreate(BaseModel):
    loan_id: int

class LoanInDB(LoanBase):
    id: int
    issue_date: datetime
    return_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True

class LoanResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True

class LoanDetailResponse(BaseModel):
    id: int
    user: UserBase
    book: BookBase
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True

class UserLoanResponse(BaseModel):
    id: int
    book: BookBase
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True

class UserLoansResponse(BaseModel):
    loans: List[UserLoanResponse]
    total: int
