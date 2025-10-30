# app/routes/photo.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.crud import user as crud_user
from app.crud import Photo as crud_photo_module
from app.schemas.Photo import PhotoCreate, PhotoUpdate, PhotoResponse, UserPhotosResponse
from app.utils.cloudinary_service import upload_photo, delete_photo as cloudinary_delete
from typing import List, Optional
import os
import uuid
import shutil
from pathlib import Path

router = APIRouter(prefix="/photos", tags=["Photos"])

# Create uploads directory if it doesn't exist (backup/fallback)
UPLOAD_DIR = Path("uploads/photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=PhotoResponse)
async def upload_photo_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    is_primary: bool = Form(False),
    order: int = Form(0)
):
    """Upload a photo file for a user to Cloudinary"""
    # Verify user exists
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Upload to Cloudinary
    try:
        # Read file content
        file_content = await file.read()

        # Upload to Cloudinary
        cloudinary_result = upload_photo(file_content, user_id)

        # Get the URL and public_id from Cloudinary
        photo_url = cloudinary_result["url"]
        public_id = cloudinary_result["public_id"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to Cloudinary: {str(e)}")

    # Create photo record with Cloudinary URL and public_id
    new_photo = crud_photo_module.create_photo(
        user_id,
        photo_url,
        is_primary,
        order,
        public_id=public_id  # Store public_id for deletion later
    )

    return new_photo.__dict__

@router.get("/files/{filename}")
async def get_photo_file(filename: str):
    """Serve a photo file"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(file_path)

@router.post("/", response_model=PhotoResponse)
def create_photo_url(photo: PhotoCreate):
    """Create photo record with URL (for external images)"""
    # Verify user exists
    user = crud_user.get_user_by_id(photo.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_photo = crud_photo_module.create_photo(
        photo.user_id,
        photo.url,
        photo.is_primary,
        photo.order
    )

    return new_photo.__dict__

@router.get("/user/{user_id}")
def get_user_photos(user_id: str):
    """Get all photos for a user"""
    photos = crud_photo_module.get_user_photos(user_id)
    return {
        "user_id": user_id,
        "photos": [p.__dict__ for p in photos]
    }

@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(photo_id: str):
    photo = crud_photo_module.get_photo_by_id(photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo.__dict__

@router.patch("/{photo_id}", response_model=PhotoResponse)
def update_photo(photo_id: str, photo_update: PhotoUpdate):
    """Update photo (change primary status or order)"""
    updated_photo = crud_photo_module.update_photo(
        photo_id,
        photo_update.is_primary,
        photo_update.order
    )

    if not updated_photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return updated_photo.__dict__

@router.delete("/{photo_id}")
def delete_photo(photo_id: str):
    """Delete a photo from Cloudinary and database"""
    photo = crud_photo_module.get_photo_by_id(photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Delete from Cloudinary if public_id exists
    if photo.public_id:
        try:
            cloudinary_delete(photo.public_id)
        except Exception as e:
            print(f"Warning: Failed to delete from Cloudinary: {str(e)}")
            # Continue with database deletion even if Cloudinary deletion fails

    # Delete from database
    crud_photo_module.delete_photo(photo_id)
    return {"message": "Photo deleted successfully"}

@router.put("/user/{user_id}/reorder")
def reorder_photos(user_id: str, photos: dict):
    """Reorder user photos"""
    photo_updates = photos.get("photos", [])

    for photo_update in photo_updates:
        photo_id = photo_update.get("photo_id")
        order = photo_update.get("order", 0)
        is_primary = photo_update.get("is_primary", False)

        if photo_id:
            crud_photo_module.update_photo(photo_id, is_primary, order)

    return {"message": "Photos reordered successfully"}
