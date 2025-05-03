import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.init_db import Base, get_db
from app.models.user import User

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

def test_create_user():
    """Test creating a new user"""
    response = client.post(
        "/api/users",
        json={"name": "Test User", "email": "test@example.com", "role": "student"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["role"] == "student"
    assert "id" in data
    assert "created_at" in data

def test_create_user_duplicate_email():
    """Test creating a user with an existing email"""
    # Create first user
    client.post(
        "/api/users",
        json={"name": "Test User", "email": "duplicate@example.com", "role": "student"}
    )
    
    # Try to create user with same email
    response = client.post(
        "/api/users",
        json={"name": "Another User", "email": "duplicate@example.com", "role": "librarian"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_get_user():
    """Test getting a user by ID"""
    # Create a user first
    create_response = client.post(
        "/api/users",
        json={"name": "Get User", "email": "get@example.com", "role": "teacher"}
    )
    user_id = create_response.json()["id"]
    
    # Get the user
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Get User"
    assert data["email"] == "get@example.com"
    assert data["role"] == "teacher"
    assert data["id"] == user_id

def test_get_user_not_found():
    """Test getting a non-existent user"""
    response = client.get("/api/users/999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_update_user():
    """Test updating a user"""
    # Create a user first
    create_response = client.post(
        "/api/users",
        json={"name": "Update User", "email": "update@example.com", "role": "student"}
    )
    user_id = create_response.json()["id"]
    
    # Update the user
    response = client.put(
        f"/api/users/{user_id}",
        json={"name": "Updated Name", "email": "updated@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == "updated@example.com"
    assert data["role"] == "student"  # Role should remain unchanged
    assert data["id"] == user_id

def test_update_user_not_found():
    """Test updating a non-existent user"""
    response = client.put(
        "/api/users/999",
        json={"name": "Updated Name"}
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_get_users():
    """Test getting a list of users"""
    # Create multiple users
    client.post("/api/users", json={"name": "User 1", "email": "user1@example.com", "role": "student"})
    client.post("/api/users", json={"name": "User 2", "email": "user2@example.com", "role": "librarian"})
    
    # Get users
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # Should have at least the two users we just created
