import secrets
import hashlib
from datetime import datetime, timedelta, timezone


def get_refresh_token_hash(token_raw:str):
    """
    Hash theo thuật toán sha 256 kèm theo mã hóa sang hệ thập lục phân (hex).
    """
    token_hash = hashlib.sha256(token_raw.encode("utf-8")).hexdigest()
    return token_hash


def create_refresh_token(expires_delta_day:timedelta):
    """
    Function tạo một chuỗi refresh_token ngẫu nhiên kèm theo thời hạn sử dụng:
    1. Tạo chuỗi raw 32 ký tự 
    2: Tạo chuỗi refresh hash bằng cách gọi hàm
    3: Khởi tạo hạn sử dụng 
    4: Trả về kết quả.
    """
    refresh_token_raw = secrets.token_urlsafe(32)
    refresh_token_hashed = get_refresh_token_hash(token_raw=refresh_token_raw)

    expire_time = datetime.now(timezone.utc) + expires_delta_day

    return {
        "refresh_token_raw":refresh_token_raw,
        "refresh_token_hashed": refresh_token_hashed,
        "expire": expire_time
    }
