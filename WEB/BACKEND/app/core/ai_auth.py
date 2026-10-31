import secrets

from fastapi import Header, status

from app.core.app_exception import AppException
from app.core.config import settings


def verify_ai_key(x_api_key: str | None = Header(default=None)):
    """
    Dependency kiểm tra header X-API-Key do module AI gửi lên.
    Sai hoặc thiếu key: trả lỗi 401.
    """
    if x_api_key is None:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="MISSING_API_KEY",
            message="❌ Thiếu header X-API-Key!"
        )

    # So sánh 2 chuỗi dưới dạng bytes
    key_from_request = x_api_key.encode("utf-8")
    key_in_config = settings.AI_POST_IMAGE_KEY.encode("utf-8")

    if not secrets.compare_digest(key_from_request, key_in_config):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_API_KEY",
            message="❌ API key không hợp lệ!"
        )