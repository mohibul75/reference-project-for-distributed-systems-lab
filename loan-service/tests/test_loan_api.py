import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from app.main import app
from app.database.init_db import Base, get_db
from app.models.loan import Loan
from app.services.external_service import ExternalServiceClient

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# Mock data for external services
mock_user = {
    "id": 1,
    "name": "Test User",
    "email": "test@example.com",
    "role": "student"
}

mock_book = {
    "id": 1,
    "title": "Test Book",
    "author": "Test Author",
    "isbn": "1234567890",
    "copies": 3,
    "available_copies": 2
}

# Mock external service calls
@pytest.fixture(autouse=True)
def mock_external_services():
    # Mock get_user method
    with patch.object(ExternalServiceClient, 'get_user', new_callable=AsyncMock) as mock_get_user:
        mock_get_user.return_value = mock_user
        
        # Mock get_book method
        with patch.object(ExternalServiceClient, 'get_book', new_callable=AsyncMock) as mock_get_book:
            mock_get_book.return_value = mock_book
            
            # Mock update_book_availability method
            with patch.object(ExternalServiceClient, 'update_book_availability', new_callable=AsyncMock) as mock_update_book:
                mock_update_book.return_value = {"id": 1, "available_copies": 1}
                
                yield

def test_create_loan():
    """Test creating a new loan"""
    due_date = (datetime.now() + timedelta(days=14)).isoformat()
    
    response = client.post(
        "/api/loans",
        json={
            "user_id": 1,
            "book_id": 1,
            "due_date": due_date
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 1
    assert data["book_id"] == 1
    assert data["status"] == "ACTIVE"
    assert "id" in data
    assert "issue_date" in data
    assert "due_date" in data

def test_return_book():
    """Test returning a book"""
    # First create a loan
    due_date = (datetime.now() + timedelta(days=14)).isoformat()
    create_response = client.post(
        "/api/loans",
        json={
            "user_id": 1,
            "book_id": 1,
            "due_date": due_date
        }
    )
    loan_id = create_response.json()["id"]
    
    # Return the book
    response = client.post(
        "/api/loans/returns",
        json={
            "loan_id": loan_id
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == loan_id
    assert data["status"] == "RETURNED"
    assert data["return_date"] is not None

def test_get_loan():
    """Test getting a loan by ID"""
    # First create a loan
    due_date = (datetime.now() + timedelta(days=14)).isoformat()
    create_response = client.post(
        "/api/loans",
        json={
            "user_id": 1,
            "book_id": 1,
            "due_date": due_date
        }
    )
    loan_id = create_response.json()["id"]
    
    # Get the loan
    response = client.get(f"/api/loans/{loan_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == loan_id
    assert "user" in data
    assert "book" in data
    assert data["user"]["id"] == 1
    assert data["book"]["id"] == 1

def test_get_user_loans():
    """Test getting a user's loans"""
    # First create a couple of loans
    due_date = (datetime.now() + timedelta(days=14)).isoformat()
    client.post(
        "/api/loans",
        json={
            "user_id": 1,
            "book_id": 1,
            "due_date": due_date
        }
    )
    
    # Get the user's loans
    response = client.get("/api/loans/user/1")
    
    assert response.status_code == 200
    data = response.json()
    assert "loans" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["loans"]) >= 1
    assert "book" in data["loans"][0]

def test_loan_not_found():
    """Test getting a non-existent loan"""
    response = client.get("/api/loans/999")
    assert response.status_code == 404
    assert "Loan not found" in response.json()["detail"]

def test_return_nonexistent_loan():
    """Test returning a non-existent loan"""
    response = client.post(
        "/api/loans/returns",
        json={
            "loan_id": 999
        }
    )
    assert response.status_code == 404
    assert "Loan not found" in response.json()["detail"]
