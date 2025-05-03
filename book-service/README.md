# Book Service

This is the Book Service component of the Smart Library System microservices architecture. It handles book inventory, search, and updates to availability.

## Features

- Add new books
- Search for books
- Update book information
- Update book availability
- Remove books from the catalog

## API Endpoints

- `POST /api/books` - Add a new book
- `GET /api/books` - Search for books
- `GET /api/books/{id}` - Get book by ID
- `PUT /api/books/{id}` - Update book information
- `PATCH /api/books/{id}/availability` - Update book availability
- `DELETE /api/books/{id}` - Remove a book

## Project Structure

```
book-service/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── books.py         # API route handlers
│   ├── core/
│   │   └── config.py            # Application configuration
│   ├── database/
│   │   └── init_db.py           # Database initialization
│   ├── exception/
│   │   └── http_exception.py    # Custom exceptions
│   ├── models/
│   │   └── book.py              # SQLAlchemy models
│   ├── schemas/
│   │   └── book.py              # Pydantic schemas
│   ├── services/
│   │   └── book_service.py      # Business logic
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
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_db
   ```

3. Run database migrations:
   ```
   alembic upgrade head
   ```

4. Start the service:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload
   ```

## Docker

Build and run with Docker:

```
docker build -t book-service .
docker run -p 8082:8082 -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/book_db book-service
```

Or use Docker Compose from the root directory:

```
docker-compose up -d book-service
```
