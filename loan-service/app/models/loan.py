from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime

from app.database.init_db import Base

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    book_id = Column(Integer, nullable=False, index=True)
    issue_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="ACTIVE", index=True)  # ACTIVE, RETURNED, OVERDUE
    
    def __repr__(self):
        return f"<Loan(id={self.id}, user_id={self.user_id}, book_id={self.book_id}, status={self.status})>"
