from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import status
from app.core.config import settings
from datetime import timedelta

from typing import Optional

from app.core.app_exception import AppException
from app.core  import jwt as jwt_service, refresh_token as refresh_service
from app.core import password 

from app.crud import refresh_token as crud_token
from app.schemas import refresh_token as schemas_token
from app.schemas import account as schemas_account
from app.crud import account as crud_account
from app.models.models import RefreshToken


# Logic đăng nhập 
def login(db: Session, input_email: EmailStr, input_password: str):
    """
    1. Kiểm tra xem có user dựa theo email không (CRUD đã tự handle ném lỗi 404 nếu không có). 
    2. Kiểm tra mật khẩu có trùng với mật khẩu lưu trong DB không.
    3. Nếu oke thì tạo access_token, refresh_token.
    """
    db_account = crud_account.get_account_by_email(db=db, email=input_email)

    is_valid_password = password.verify_password(plain_password=input_password, hashed_password=db_account.password_hash)
    if not is_valid_password:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="WRONG_PASSWORD",
            message=f"❌ Email hoặc mật khẩu chưa chính xác. Vui lòng kiếm tra lại!"
        )
        
    # TẠO ACCESS TOKEN
    # Chọn phần data muốn lưu vào JWT - payload - chứa thông tin -- Email và id user
    data = {
        "sub": db_account.email,
        "data": db_account.id
    }
    jwt_access_token = jwt_service.create_jwt_token(data= data, expires_delta=None)

    # TẠO REFRESH TOKEN
    expires_delta_day = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_data = refresh_service.create_refresh_token(expires_delta_day=expires_delta_day)

    create_token = schemas_token.Create(
        account_id=db_account.id,
        token_hash=refresh_data["refresh_token_hashed"],
        expires_at=refresh_data["expire"]
    )
    crud_token.create(db=db, create_data=create_token)
    current_account = schemas_account.Response(
        id=db_account.id,
        email=db_account.email,
        username=db_account.username
    )
    # Trả về cho router
    return {
        "access_token": jwt_access_token,
        "refresh_token_raw": refresh_data["refresh_token_raw"],
        # đổi ra giây để lưu lên cookie
        "expires_delta_day": expires_delta_day.total_seconds(),
        "user_info":current_account
    }

# Helper nội bộ hỗ trợ trả lỗi nếu có xâm nhập 
def _check_token_reused(db: Session, db_token: RefreshToken):
    """
    Khi phát hiện một token được gửi đến có giá trị revoked sẵn là True
    -> Chứng tỏ có ai đó đang sử dụng một refresh cũ.
    -> đã có người xâm nhập vì token này không dùng nữa, chẳng qua chưa hết hạn thôi.
    -> revoked = True toàn bộ
    -> Trả lỗi
    """
    if db_token.revoked == True:
        crud_token.update_all_revoked(db=db, user_id=db_token.user_id)
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_REFRESH_TOKEN",
            message=f"❌ Phiên đăng nhập không hợp lệ, vui lòng đăng nhập lại."
        )

# logic yêu cầu cấp access token
def refresh_access(db: Session, refresh_token: Optional[str] = None ):
    """
    Func xử lý logic khi FE call API yêu cầu 1 access_token mới - gọi ngầm
    1. Nhận refresh_token ở request 
    2. check refresh token tương ứng với user id nào, refresh token nào. 
    3. Nếu tồn tại thì kiểm tra xem revoke có true ko
    4. Nếu revoke = false -> đổi thành True 
    -> tạo mới refresh và access_token
    5. Tiện thể gọi hàm làm sạch bảng token này. 
    6. trả về cho access_token refresh raw để bên router lưu lên cookie. 
    """
    # 1. Nhận refresh_token ở request 
    if refresh_token is None:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="MISSING_REFRESH_TOKEN",
            message=f"❌ Không tìm thấy phiên đăng nhập, vui lòng đăng nhập lại."
        )
    
    # 2. check refresh token tương ứng với user id nào, refresh token nào.
    refresh_token_hash = refresh_service.get_refresh_token_hash(token_raw=refresh_token)
    db_token = crud_token.get_by_token(db=db, token_hash=refresh_token_hash)
    db_account = crud_account.get_account(db=db, target_id=db_token.account_id)

    # 3. Nếu tồn tại thì kiểm tra xem revoke có true ko 
    _check_token_reused(db=db, db_token=db_token)

    # 4. Nếu revoke = false -> đổi thành True 
    crud_token.update_revoked(db=db, db_token=db_token)

    # -> tạo mới access_token  
    data = {
        "data": db_token.account_id,
        "sub" : db_account.id
    }
    expires_delta_minute = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_service.create_jwt_token(data=data, expires_delta=expires_delta_minute)

    # và refresh token
    expires_delta_day = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_data = refresh_service.create_refresh_token(expires_delta_day=expires_delta_day)
    create_token = schemas_token.Create(
        account_id=db_token.account_id,
        token_hash= refresh_data["refresh_token_hashed"],
        expires_at= refresh_data["expire"]
    )
    crud_token.create(db=db, create_data=create_token)

    # 5. Tiện thể gọi hàm làm sạch bảng token này.
    crud_token.clean(db=db)

    # trả về cho access_token refresh raw để bên router lưu lên cookie
    return {
        "access_token": access_token,
        "refresh_token_raw": refresh_data["refresh_token_raw"],
        # đổi ra giây để lưu lên cookie
        "expires_delta_day": int(expires_delta_day.total_seconds())
    }
   
# logic log out
def logout(db:Session, refresh_token:str):
    """
    Function xử lý log out cho từng trình duyệt, tức chỉ đăng xuất đúng trên trình duyệt đó. 

    1. Đọc Refresh Token từ cookie, hash, tìm đúng row
    2. Kiểm tra Revoke - nếu False thid chuyển True bình thường, còn 
    nếu True sẵn thì -> Revoked hết trên cùng 1 user 
    (ảnh hưởng khi dùng thiết bị vì chưa thiết kế đa thiết bị - nhưng chịu r, cách này là ổn nhất)
    3. Trả về kết quả tương ứng. 
    """ 
    # 1. Nhận refresh_token ở request 
    if refresh_token is None:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="MISSING_REFRESH_TOKEN",
            message=f"❌ Không tìm thấy phiên đăng nhập, vui lòng đăng nhập lại."
        )
    
    refresh_token_hash = refresh_service.get_refresh_token_hash(token_raw=refresh_token)
    db_token = crud_token.get_by_token(db=db, token_hash=refresh_token_hash)

    _check_token_reused(db=db, db_token=db_token)

    crud_token.update_revoked(db=db, db_token=db_token)

    return

# logic dọn dẹp token
def clean_token(db:Session):
    """
    service hỗ trợ chủ động dọn dẹp bảng thay vì phải thông qua 
    cấp access token mới dọn, đó chỉ là tiện thể.
    """
    crud_token.clean(db=db)
    return


