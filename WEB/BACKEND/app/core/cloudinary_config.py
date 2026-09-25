import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.core.config import settings
from app.core.exception import AppException
from fastapi import status

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

# Tải ảnh lên cloudinary
def upload_image(folder_name ,file):
    """Upload ảnh lên cloudinary. Trả về secure_url - url ảnh, public_id: id ảnh trên cloud """
    try:
        result = cloudinary.uploader.upload(
            file, folder = folder_name
        )
        return {
            "secure_url": result["secure_url"],
            "public_id":  result["public_id"]
        }
    except Exception as e:
        print(f"[Cloudinary upload error]: {e}")
        raise AppException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            error_code="CLOUDINARY_UPLOAD_FAILED",
            message= f"❌ Uploading image failed. Please check and try again. [{e}]"
        )

# Xóa ảnh trên cloudinary       
def destroy_image(public_id):
    """ Xóa ảnh theo public_id -> Tránh các file ảnh rác -> tốn dung lượng bản free!"""
    try:
        cloudinary.uploader.destroy(public_id)
        return
    except Exception as e:
        print(f"[Cloudinary upload error]: {e}")
        raise AppException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            error_code="CLOUDINARY_UPLOAD_FAILED",
            message= f"❌ Uploading image failed. Please check and try again. [{e}]"
        )

# Xóa folder
def delete_folder(folder_name):
    try:
        cloudinary.api.delete_folder(folder_name)
        return
    except Exception as e:
        print(f"[Cloudinary upload error]: {e}")
        raise AppException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            error_code="CLOUDINARY_UPLOAD_FAILED",
            message= f"❌ Uploading image failed. Please check and try again. [{e}]"
        )
        