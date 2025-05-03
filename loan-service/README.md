# Loan Service

This is the Loan Service component of the Smart Library System microservices architecture. It handles book loans, returns, and communicates with both the User Service and Book Service.

## Features

- Issue books to users
- Return books
- View loan details
- View user loan history

## API Endpoints

- `POST /api/loans` - Issue a book to a user
- `POST /api/loans/returns` - Return a borrowed book
- `GET /api/loans/user/{user_id}` - Get a user's loan history
- `GET /api/loans/{id}` - Get loan details

## Inter-Service Communication

The Loan Service communicates with:

1. **User Service** - To verify user existence and get user details
2. **Book Service** - To check book availability, update book availability during issue and return

## Project Structure

```
loan-service/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── loans.py         # API route handlers
│   ├── core/
│   │   └── config.py            # Application configuration
│   ├── database/
│   │   └── init_db.py           # Database initialization
│   ├── exception/
│   │   └── http_exception.py    # Custom exceptions
│   ├── models/
│   │   └── loan.py              # SQLAlchemy models
│   ├── schemas/
│   │   └── loan.py              # Pydantic schemas
│   ├── services/
│   │   ├── external_service.py  # Client for external services
│   │   └── loan_service.py      # Business logic
│   └── main.py                  # Application entry point
├── migrations/                  # Alembic migrations
├── tests/                       # Test files
├── .env                         # Environment variables
├── alembic.ini                  # Alembic configuration
├── Dockerfile                   # Docker configuration
└── requirements.txt             # Dependencies
```

## Running Locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/loan_db
   export USER_SERVICE_URL=http://localhost:8081
   export BOOK_SERVICE_URL=http://localhost:8082
   ```

3. Run database migrations:
   ```
   alembic upgrade head
   ```

4. Start the service:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8083 --reload
   ```

## Docker

Build and run with Docker:

```
docker build -t loan-service .
docker run -p 8083:8083 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/loan_db \
  -e USER_SERVICE_URL=http://host.docker.internal:8081 \
  -e BOOK_SERVICE_URL=http://host.docker.internal:8082 \
  loan-service
```

Or use Docker Compose from the root directory:

```
docker-compose up -d loan-service
```

## Error Handling

The Loan Service implements robust error handling for various scenarios:

- If the User Service is unavailable, returns a 503 Service Unavailable response
- If the Book Service is unavailable, returns a 503 Service Unavailable response
- If the user doesn't exist, returns a 404 Not Found response
- If the book doesn't exist or has no available copies, returns a 400 Bad Request response
