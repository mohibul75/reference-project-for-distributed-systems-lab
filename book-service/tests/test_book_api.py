import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.init_db import Base, get_db
from app.models.book import Book

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

def test_create_book():
    """Test creating a new book"""
    response = client.post(
        "/api/books",
        json={
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "1234567890123",
            "copies": 3
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["isbn"] == "1234567890123"
    assert data["copies"] == 3
    assert data["available_copies"] == 3
    assert "id" in data
    assert "created_at" in data

def test_create_book_duplicate_isbn():
    """Test creating a book with an existing ISBN"""
    # Create first book
    client.post(
        "/api/books",
        json={
            "title": "First Book",
            "author": "First Author",
            "isbn": "9876543210123",
            "copies": 2
        }
    )
    
    # Try to create book with same ISBN
    response = client.post(
        "/api/books",
        json={
            "title": "Second Book",
            "author": "Second Author",
            "isbn": "9876543210123",
            "copies": 1
        }
    )
    assert response.status_code == 400
    assert "ISBN already registered" in response.json()["detail"]

def test_get_book():
    """Test getting a book by ID"""
    # Create a book first
    create_response = client.post(
        "/api/books",
        json={
            "title": "Get Book",
            "author": "Get Author",
            "isbn": "5555555555555",
            "copies": 1
        }
    )
    book_id = create_response.json()["id"]
    
    # Get the book
    response = client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get Book"
    assert data["author"] == "Get Author"
    assert data["isbn"] == "5555555555555"
    assert data["id"] == book_id

def test_get_book_not_found():
    """Test getting a non-existent book"""
    response = client.get("/api/books/999")
    assert response.status_code == 404
    assert "Book not found" in response.json()["detail"]

def test_update_book():
    """Test updating a book"""
    # Create a book first
    create_response = client.post(
        "/api/books",
        json={
            "title": "Update Book",
            "author": "Update Author",
            "isbn": "4444444444444",
            "copies": 2
        }
    )
    book_id = create_response.json()["id"]
    
    # Update the book
    response = client.put(
        f"/api/books/{book_id}",
        json={
            "title": "Updated Title",
            "copies": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Update Author"  # Unchanged
    assert data["copies"] == 5
    assert data["available_copies"] == 5  # Should be updated with copies
    assert data["id"] == book_id

def test_update_book_availability():
    """Test updating book availability"""
    # Create a book first
    create_response = client.post(
        "/api/books",
        json={
            "title": "Availability Book",
            "author": "Availability Author",
            "isbn": "3333333333333",
            "copies": 3
        }
    )
    book_id = create_response.json()["id"]
    
    # Update availability (decrement)
    response = client.patch(
        f"/api/books/{book_id}/availability",
        json={
            "available_copies": 1,
            "operation": "decrement"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["available_copies"] == 2
    
    # Update availability (set)
    response = client.patch(
        f"/api/books/{book_id}/availability",
        json={
            "available_copies": 1,
            "operation": "set"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["available_copies"] == 1

def test_search_books():
    """Test searching for books"""
    # Create multiple books
    client.post(
        "/api/books",
        json={
            "title": "Python Programming",
            "author": "John Doe",
            "isbn": "1111111111111",
            "copies": 2
        }
    )
    client.post(
        "/api/books",
        json={
            "title": "Advanced Python",
            "author": "Jane Smith",
            "isbn": "2222222222222",
            "copies": 1
        }
    )
    
    # Search by title
    response = client.get("/api/books?search=Python")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["books"]) >= 2
    
    # Search by author
    response = client.get("/api/books?search=Jane")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["books"]) >= 1
    assert any(book["author"] == "Jane Smith" for book in data["books"])

def test_delete_book():
    """Test deleting a book"""
    # Create a book first
    create_response = client.post(
        "/api/books",
        json={
            "title": "Delete Book",
            "author": "Delete Author",
            "isbn": "6666666666666",
            "copies": 1
        }
    )
    book_id = create_response.json()["id"]
    
    # Delete the book
    response = client.delete(f"/api/books/{book_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/books/{book_id}")
    assert get_response.status_code == 404
