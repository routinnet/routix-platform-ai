from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
import uuid
import aiofiles
from PIL import Image
import io

from src.core.database import get_db
from src.core.config import settings
from src.models.user import User
from src.api.dependencies import get_current_active_user

router = APIRouter()


def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file."""
    
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        )
    
    # Check file extension
    if file.filename:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.allowed_file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed types: {settings.allowed_file_types}"
            )
    
    return True


async def optimize_image(file_path: str, max_width: int = 1920, max_height: int = 1080, quality: int = 85):
    """Optimize uploaded image."""
    
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
            
    except Exception as e:
        # If optimization fails, keep original file
        pass


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a file."""
    
    # Validate file
    validate_file(file)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Create user directory if it doesn't exist
    user_dir = os.path.join(settings.upload_dir, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    
    # Full file path
    file_path = os.path.join(user_dir, unique_filename)
    
    try:
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Optimize image if it's an image file
        if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
            await optimize_image(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        # Return file info
        file_url = f"/uploads/{current_user.id}/{unique_filename}"
        
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_url": file_url,
            "file_size": file_size,
            "content_type": file.content_type,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        # Clean up file if something went wrong
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload multiple files."""
    
    if len(files) > 10:  # Limit to 10 files per request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per request"
        )
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            # Validate file
            validate_file(file)
            
            # Generate unique filename
            file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else '.jpg'
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(settings.upload_dir, str(current_user.id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Full file path
            file_path = os.path.join(user_dir, unique_filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Optimize image if it's an image file
            if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                await optimize_image(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_url = f"/uploads/{current_user.id}/{unique_filename}"
            
            uploaded_files.append({
                "filename": unique_filename,
                "original_filename": file.filename,
                "file_path": file_path,
                "file_url": file_url,
                "file_size": file_size,
                "content_type": file.content_type
            })
            
        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "uploaded_files": uploaded_files,
        "failed_files": failed_files,
        "total_uploaded": len(uploaded_files),
        "total_failed": len(failed_files)
    }


@router.delete("/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a user's uploaded file."""
    
    # Construct file path
    file_path = os.path.join(settings.upload_dir, str(current_user.id), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        os.remove(file_path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/")
async def list_user_files(
    current_user: User = Depends(get_current_active_user)
):
    """List user's uploaded files."""
    
    user_dir = os.path.join(settings.upload_dir, str(current_user.id))
    
    if not os.path.exists(user_dir):
        return {"files": []}
    
    files = []
    for filename in os.listdir(user_dir):
        file_path = os.path.join(user_dir, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            file_url = f"/uploads/{current_user.id}/{filename}"
            
            files.append({
                "filename": filename,
                "file_url": file_url,
                "file_size": file_size,
                "created_at": os.path.getctime(file_path)
            })
    
    return {"files": files}
