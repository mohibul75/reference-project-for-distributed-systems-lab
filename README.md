# Smart Library System - Microservices Architecture

This project implements a Smart Library System using a microservices architecture with Python FastAPI. The system is divided into three independent services, each responsible for a specific domain:

1. **User Service** - Handles user registration, profile management, and user-related queries
2. **Book Service** - Manages book inventory, search, and updates to availability
3. **Loan Service** - Issues and returns books by communicating with both User Service and Book Service

## Architecture Overview

- Each service is built with FastAPI
- Each service has its own PostgreSQL database
- Services communicate via HTTP/REST APIs
- Each service runs in its own container
- No shared databases between services

## Services and Endpoints

### User Service
- Base Path: `/api/users`
- Database: `user_db`
- Endpoints:
  - `POST /api/users` - Create a new user
  - `GET /api/users/{id}` - Get user by ID
  - `PUT /api/users/{id}` - Update user information

### Book Service
- Base Path: `/api/books`
- Database: `book_db`
- Endpoints:
  - `POST /api/books` - Add a new book
  - `GET /api/books` - Search for books
  - `GET /api/books/{id}` - Get book by ID
  - `PUT /api/books/{id}` - Update book information
  - `PATCH /api/books/{id}/availability` - Update book availability
  - `DELETE /api/books/{id}` - Remove a book

### Loan Service
- Base Path: `/api/loans`
- Database: `loan_db`
- Endpoints:
  - `POST /api/loans` - Issue a book to a user
  - `POST /api/returns` - Return a borrowed book
  - `GET /api/loans/user/{user_id}` - Get user's loan history
  - `GET /api/loans/{id}` - Get loan details

## Setup and Running

### Prerequisites
- Docker and Docker Compose
- Python 3.9+

### Running the Application
1. Clone the repository
2. Navigate to the project root directory
3. Run `docker-compose up -d`
4. Access the services:
   - User Service: http://localhost:8081/api/users
   - Book Service: http://localhost:8082/api/books
   - Loan Service: http://localhost:8083/api/loans

## Development

Each service is a FastAPI application with its own PostgreSQL database. The services communicate with each other using HTTP clients.

## Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation and settings management
- **Alembic**: Database migrations
- **PostgreSQL**: Relational database
- **Docker**: Containerization
- **Pytest**: Testing framework

## Testing

Each service has its own unit and integration tests. There are also end-to-end tests that verify the interaction between services.
