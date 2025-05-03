from fastapi import HTTPException, status

class BookNotFoundException(HTTPException):
    def __init__(self, detail: str = "Book not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ISBNAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "ISBN already registered"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class NoAvailableCopiesException(HTTPException):
    def __init__(self, detail: str = "No available copies"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class InvalidRequestException(HTTPException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class DatabaseException(HTTPException):
    def __init__(self, detail: str = "Database error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
