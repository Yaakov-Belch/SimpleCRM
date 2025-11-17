"""Authentication routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas import AuthResponseSchema, UserLoginSchema, UserRegisterSchema
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="""
    Register a new user account and automatically create a session.

    The user will be automatically logged in after successful registration
    with a session valid for 7 days.

    **Authentication:** Not required (public endpoint)

    **Request Body:**
    - `full_name` (string, required): User's full name (max 255 characters)
    - `email` (string, required): Valid email address (unique, case-insensitive)
    - `password` (string, required): Password (minimum 8 characters)

    **Success Response (201):**
    ```json
    {
      "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "created_at": "2025-11-17T10:30:00Z",
        "updated_at": "2025-11-17T10:30:00Z"
      },
      "session_token": "abc123...xyz"
    }
    ```

    **Error Responses:**
    - `400 Bad Request`: Invalid input data (malformed email, password too short, etc.)
    - `409 Conflict`: Email already exists in the database
    - `500 Internal Server Error`: Unexpected server error
    """
)
def register(
    user_data: UserRegisterSchema,
    db: DBSession = Depends(get_db)
):
    """Register a new user and create session."""
    try:
        user, session = AuthService.register(
            db,
            full_name=user_data.full_name,
            email=user_data.email,
            password=user_data.password
        )

        return {
            "user": user,
            "session_token": session.session_token
        }
    except ValueError as e:
        if "Email already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=AuthResponseSchema,
    summary="Login with email and password",
    description="""
    Authenticate a user and create a new session.

    Creates a new session valid for 7 days. Multiple concurrent sessions
    are allowed (logging in does not invalidate existing sessions).

    **Authentication:** Not required (public endpoint)

    **Request Body:**
    - `email` (string, required): User's email address (case-insensitive)
    - `password` (string, required): User's password

    **Success Response (200):**
    ```json
    {
      "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "created_at": "2025-11-17T10:30:00Z",
        "updated_at": "2025-11-17T10:30:00Z"
      },
      "session_token": "abc123...xyz"
    }
    ```

    **Error Responses:**
    - `400 Bad Request`: Missing required fields
    - `401 Unauthorized`: Invalid email or password (generic message for security)
    - `500 Internal Server Error`: Unexpected server error

    **Security Note:** Error message is intentionally generic ("Invalid email or password")
    to prevent email enumeration attacks.
    """
)
def login(
    credentials: UserLoginSchema,
    db: DBSession = Depends(get_db)
):
    """Login user and create session."""
    result = AuthService.login(
        db,
        email=credentials.email,
        password=credentials.password
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user, session = result

    return {
        "user": user,
        "session_token": session.session_token
    }


@router.post(
    "/logout",
    summary="Logout and delete current session",
    description="""
    Logout the current user by deleting their session.

    Only deletes the current session. Other sessions for the same user
    (from other devices/browsers) will remain active.

    **Authentication:** Required (Bearer token in Authorization header)

    **Headers:**
    - `Authorization` (required): Bearer token, e.g., "Bearer abc123...xyz"

    **Success Response (200):**
    ```json
    {
      "message": "Logged out successfully"
    }
    ```

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `500 Internal Server Error`: Unexpected server error
    """
)
def logout(
    token: Optional[str] = Header(None, alias="Authorization"),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Logout user by deleting current session."""
    # Extract token from "Bearer {token}" format
    if token and token.startswith("Bearer "):
        session_token = token[7:]
        AuthService.logout(db, session_token)

    return {"message": "Logged out successfully"}
