"""User profile routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas import UserResponseSchema, UserUpdateSchema
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponseSchema,
    summary="Get current user's profile",
    description="""
    Retrieve the profile of the currently authenticated user.

    **Authentication:** Required (Bearer token in Authorization header)

    **Headers:**
    - `Authorization` (required): Bearer token, e.g., "Bearer abc123...xyz"

    **Success Response (200):**
    ```json
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "created_at": "2025-11-17T10:30:00Z",
      "updated_at": "2025-11-17T10:30:00Z"
    }
    ```

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `500 Internal Server Error`: Unexpected server error

    **Security Note:** The `hashed_password` field is never included in the response.
    """
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponseSchema,
    summary="Update current user's profile",
    description="""
    Update the profile of the currently authenticated user.

    Supports partial updates - only provided fields will be updated.
    You can update any combination of full_name, email, and/or password.

    **Authentication:** Required (Bearer token in Authorization header)

    **Headers:**
    - `Authorization` (required): Bearer token, e.g., "Bearer abc123...xyz"

    **Request Body (all fields optional):**
    - `full_name` (string, optional): User's full name (max 255 characters)
    - `email` (string, optional): Valid email address (unique, case-insensitive)
    - `password` (string, optional): New password (minimum 8 characters)

    **Success Response (200):**
    ```json
    {
      "id": 1,
      "email": "newemail@example.com",
      "full_name": "Jane Doe",
      "created_at": "2025-11-17T10:30:00Z",
      "updated_at": "2025-11-17T10:35:00Z"
    }
    ```

    **Error Responses:**
    - `400 Bad Request`: Invalid input data (malformed email, password too short, etc.)
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `409 Conflict`: Email already exists (belongs to another user)
    - `500 Internal Server Error`: Unexpected server error

    **Examples:**

    Update only full name:
    ```json
    {
      "full_name": "Jane Doe"
    }
    ```

    Update only email:
    ```json
    {
      "email": "newemail@example.com"
    }
    ```

    Update only password:
    ```json
    {
      "password": "newpassword123"
    }
    ```

    Update multiple fields:
    ```json
    {
      "full_name": "Jane Doe",
      "email": "jane@example.com",
      "password": "newpassword123"
    }
    ```

    **Security Notes:**
    - Password will be hashed before storage (bcrypt with 12 rounds)
    - The `hashed_password` field is never included in the response
    - Email uniqueness is enforced (case-insensitive)
    """
)
def update_current_user_profile(
    update_data: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Update current user's profile (supports partial updates)."""
    # Convert Pydantic model to dict, excluding unset fields
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        # No fields to update, return current user
        return current_user

    try:
        updated_user = UserService.update_user(db, current_user.id, update_dict)
        return updated_user
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
