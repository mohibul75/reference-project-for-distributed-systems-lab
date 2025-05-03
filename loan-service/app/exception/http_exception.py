from fastapi import HTTPException, status

class LoanNotFoundException(HTTPException):
    def __init__(self, detail: str = "Loan not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UserNotFoundException(HTTPException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BookNotFoundException(HTTPException):
    def __init__(self, detail: str = "Book not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class NoAvailableCopiesException(HTTPException):
    def __init__(self, detail: str = "No available copies of the book"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ServiceUnavailableException(HTTPException):
    def __init__(self, service: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} service is currently unavailable"
        )

class InvalidRequestException(HTTPException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class DatabaseException(HTTPException):
    def __init__(self, detail: str = "Database error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
