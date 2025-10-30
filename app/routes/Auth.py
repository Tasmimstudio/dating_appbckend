# app/routes/Auth.py
from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.crud import user as crud_user
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas.User import UserCreate
import secrets

# ✅ Removed prefix from router
router = APIRouter(tags=["Authentication"])

# ---------- Response Models ----------
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class LoginRequest(BaseModel):
    email: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class DeleteAccountRequest(BaseModel):
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    reset_code: str
    new_password: str

# ---------- Register ----------
@router.post("/register", response_model=Token)
def register(user: UserCreate):
    """Register a new user and return access token"""
    try:
        existing_user = crud_user.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = get_password_hash(user.password)

        user_dict = user.model_dump() if hasattr(user, 'model_dump') else user.dict()
        user_dict['password_hash'] = hashed_password

        # Capitalize first letter of name
        if 'name' in user_dict and user_dict['name']:
            user_dict['name'] = user_dict['name'].strip().title()

        new_user = crud_user.create_user_with_password(user_dict)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.user_id},
            expires_delta=access_token_expires
        )

        user_dict = new_user.__dict__.copy()
        user_dict.pop("password_hash", None)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

# ---------- Login ----------
@router.post("/login", response_model=Token)
def login(credentials: LoginRequest):
    """Login user and return access token"""
    try:
        user = crud_user.get_user_by_email(credentials.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.user_id},
            expires_delta=access_token_expires
        )

        user_dict = user.__dict__.copy()
        user_dict.pop("password_hash", None)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )

# ---------- Forgot Password ----------
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    """Generate password reset code for user"""
    try:
        user = crud_user.get_user_by_email(request.email)

        if not user:
            # Return success even if user doesn't exist (security best practice)
            return {
                "message": "If an account exists with this email, a password reset link has been sent."
            }

        # Generate 6-digit reset code
        reset_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])

        # Store reset code in database with expiration (30 minutes)
        from app.config import get_db
        session = get_db()

        try:
            expires_at = datetime.utcnow() + timedelta(minutes=30)

            query = """
            MATCH (u:User {user_id: $user_id})
            SET u.reset_code = $reset_code,
                u.reset_code_expires = datetime($expires_at)
            RETURN u
            """

            result = session.run(query, {
                "user_id": user.user_id,
                "reset_code": reset_code,
                "expires_at": expires_at.isoformat()
            })

            if not result.single():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate reset code"
                )
        finally:
            session.close()

        # Send password reset email
        from app.utils.email import send_password_reset_email

        email_sent = send_password_reset_email(
            to_email=request.email,
            reset_code=reset_code,
            user_name=user.name
        )

        if not email_sent:
            print(f"⚠️ Failed to send email, but code is still valid")
            print(f"🔐 Password reset code for {request.email}: {reset_code}")

        return {
            "message": "If an account exists with this email, a password reset code has been sent."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Forgot password error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process request: {str(e)}"
        )

# ---------- Reset Password ----------
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    """Reset password using reset code"""
    try:
        user = crud_user.get_user_by_email(request.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        from app.config import get_db
        session = get_db()

        try:
            # Verify reset code and check expiration
            query = """
            MATCH (u:User {user_id: $user_id})
            WHERE u.reset_code = $reset_code
            AND datetime(u.reset_code_expires) > datetime($now)
            RETURN u
            """

            result = session.run(query, {
                "user_id": user.user_id,
                "reset_code": request.reset_code,
                "now": datetime.utcnow().isoformat()
            })

            if not result.single():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset code"
                )

            # Validate new password
            if len(request.new_password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters long"
                )

            # Hash new password and clear reset code
            new_password_hash = get_password_hash(request.new_password)

            update_query = """
            MATCH (u:User {user_id: $user_id})
            SET u.password_hash = $password_hash,
                u.reset_code = null,
                u.reset_code_expires = null
            RETURN u
            """

            result = session.run(update_query, {
                "user_id": user.user_id,
                "password_hash": new_password_hash
            })

            if not result.single():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to reset password"
                )
        finally:
            session.close()

        return {"message": "Password reset successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )

# ---------- Change Password ----------
@router.put("/change-password/{user_id}")
def change_password(user_id: str, request: ChangePasswordRequest):
    """Change user password"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify current password
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )

    # Hash and update password
    new_password_hash = get_password_hash(request.new_password)
    from app.config import get_db
    session = get_db()

    try:
        query = """
        MATCH (u:User {user_id: $user_id})
        SET u.password_hash = $password_hash
        RETURN u
        """

        result = session.run(query, {
            "user_id": user_id,
            "password_hash": new_password_hash
        })

        if not result.single():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        return {"message": "Password updated successfully"}
    finally:
        session.close()

# ---------- Delete Account ----------
@router.delete("/delete-account/{user_id}")
def delete_account(user_id: str, request: DeleteAccountRequest):
    """Delete user account"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    from app.config import get_db
    session = get_db()

    try:
        # Delete all user data (messages, swipes, matches, photos, etc.)
        query = """
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (u)-[r]-()
        OPTIONAL MATCH (p:Photo)-[:BELONGS_TO]->(u)
        OPTIONAL MATCH (m:Message) WHERE m.sender_id = $user_id OR m.receiver_id = $user_id
        DELETE r, p, m, u
        RETURN count(u) as deleted_count
        """

        result = session.run(query, {"user_id": user_id})
        record = result.single()

        if not record or record["deleted_count"] == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete account"
            )

        return {"message": "Account deleted successfully"}
    finally:
        session.close()
