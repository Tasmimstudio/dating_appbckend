# app/utils/cloudinary_service.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import cloudinary (optional dependency)
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
except ImportError:
    CLOUDINARY_AVAILABLE = False
    print("WARNING: cloudinary module not installed. Photo upload features will be disabled.")
    print("Install with: pip install cloudinary")

def upload_photo(file_content, user_id: str, folder: str = "dating_app/photos"):
    """
    Upload a photo to Cloudinary

    Args:
        file_content: The file content (bytes or file-like object)
        user_id: User ID for organizing uploads
        folder: Cloudinary folder path

    Returns:
        dict: Upload result containing URL and public_id
    """
    if not CLOUDINARY_AVAILABLE:
        raise Exception("Cloudinary is not available. Please install it with: pip install cloudinary")

    try:
        # Upload to Cloudinary with transformation options
        result = cloudinary.uploader.upload(
            file_content,
            folder=f"{folder}/{user_id}",
            transformation=[
                {'width': 1000, 'height': 1000, 'crop': 'limit'},  # Max dimensions
                {'quality': 'auto:good'},  # Auto quality optimization
                {'fetch_format': 'auto'}  # Auto format (WebP when supported)
            ],
            resource_type="image"
        )

        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format"),
            "bytes": result.get("bytes")
        }
    except Exception as e:
        raise Exception(f"Failed to upload to Cloudinary: {str(e)}")


def delete_photo(public_id: str):
    """
    Delete a photo from Cloudinary

    Args:
        public_id: The Cloudinary public_id of the photo to delete

    Returns:
        dict: Deletion result
    """
    if not CLOUDINARY_AVAILABLE:
        raise Exception("Cloudinary is not available. Please install it with: pip install cloudinary")

    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        return result
    except Exception as e:
        raise Exception(f"Failed to delete from Cloudinary: {str(e)}")


def get_optimized_url(public_id: str, width: int = None, height: int = None):
    """
    Get an optimized URL for a Cloudinary image

    Args:
        public_id: The Cloudinary public_id
        width: Optional width for transformation
        height: Optional height for transformation

    Returns:
        str: Optimized image URL
    """
    if not CLOUDINARY_AVAILABLE:
        raise Exception("Cloudinary is not available. Please install it with: pip install cloudinary")

    try:
        transformation = []

        if width or height:
            crop_params = {'crop': 'fill'}
            if width:
                crop_params['width'] = width
            if height:
                crop_params['height'] = height
            transformation.append(crop_params)

        transformation.extend([
            {'quality': 'auto:good'},
            {'fetch_format': 'auto'}
        ])

        url = cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation)
        return url
    except Exception as e:
        raise Exception(f"Failed to generate optimized URL: {str(e)}")
