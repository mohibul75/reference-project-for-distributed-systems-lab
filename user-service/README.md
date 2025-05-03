# User Service

This is the User Service component of the Smart Library System microservices architecture. It handles user registration, profile management, and user-related queries.

## Features

- Create new users
- Retrieve user information
- Update user profiles
- List all users

## API Endpoints

- `POST /api/users` - Create a new user
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user information
- `GET /api/users` - List all users

## Project Structure

```
user-service/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── users.py    # API route handlers
│   ├── core/
│   │   └── config.py       # Application configuration
│   ├── database/
│   │   └── init_db.py      # Database initialization
│   ├── exception/
│   │   └── http_exception.py # Custom exceptions
│   ├── models/
│   │   └── user.py         # SQLAlchemy models
│   ├── schemas/
│   │   └── user.py         # Pydantic schemas
│   ├── services/
│   │   └── user_service.py # Business logic
│   └── main.py             # Application entry point
├── migrations/             # Alembic migrations
├── tests/                  # Test files
├── .env                    # Environment variables
├── alembic.ini             # Alembic configuration
├── Dockerfile              # Docker configuration
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Dependencies
```

## Running Locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/user_db
   ```

3. Run database migrations:
   ```
   alembic upgrade head
   ```

4. Start the service:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
   ```

## Running Tests

```
pytest
```

## Docker

Build and run with Docker:

```
docker build -t user-service .
docker run -p 8081:8081 -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/user_db user-service
```

Or use Docker Compose from the root directory:

```
docker-compose up -d user-service
```
