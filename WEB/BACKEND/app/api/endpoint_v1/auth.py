from fastapi import APIRouter, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from typing import Optional

from app.services import auth as logic_auth
from app.core.config import settings
from app.schemas import auth as schemas_auth
from app.db_connection import connect_db
from app.core.app_response import AppResponse
from app.schemas import account as schemas_account
from app.models.models import Account
from app.core import jwt as jwt_service

BASE_URL= settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/auth",
    tags= ["Authentication"]
)

@router.post("/login")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db : Session = Depends(connect_db)
):
    result = logic_auth.login(db= db, input_email=form_data.username, input_password=form_data.password)

    refresh_token_key = settings.REFRESH_TOKEN_KEY_COOKIE
    response.set_cookie(
        key=refresh_token_key,
        value=result["refresh_token_raw"],
        httponly=True,
        secure=True, # Chỉ gửi dữ liệu cookie qua HTTPS - bảo mật hơn
        samesite="none", # Khác domain giữa FE và BE
        path=BASE_URL+"/auth",
        max_age=result["expires_delta_day"],
    )
    return {
        "access_token":result["access_token"],
        "token_type": "bearer",
        "message": f"🎉 Bạn đã đăng nhập thành công.",
        "user_info":result["user_info"]
    }
    # return AppResponse( data=data, message=f"🎉 Bạn đã đăng nhập thành công.")

@router.post("/refresh-access-token")
def refresh_access(
    response: Response,
    db: Session = Depends(connect_db),
    refresh_token: Optional[str] = Cookie(default=None, alias=settings.REFRESH_TOKEN_KEY_COOKIE)
):
    result = logic_auth.refresh_access(db=db, refresh_token=refresh_token)
    refresh_token_key = settings.REFRESH_TOKEN_KEY_COOKIE
    response.set_cookie(
        key=refresh_token_key,
        value=result["refresh_token_raw"],
        httponly=True,
        secure=True, # Chỉ gửi dữ liệu cookie qua HTTPS - bảo mật hơn
        samesite="none", # Khác domain giữa FE và BE
        path=BASE_URL+"/auth",
        max_age=result["expires_delta_day"],
    )
    return{
        "access_token":result["access_token"],
        "token_type": "bearer",
        "message": f"🎉 Tạo mới phiên đăng nhập thành công.",
    }

@router.post("/logout")
def log_out(
    response: Response,
    db:Session = Depends(connect_db),
    refresh_token: Optional[str] = Cookie(default=None, alias=settings.REFRESH_TOKEN_KEY_COOKIE)
):
    logic_auth.logout(db=db, refresh_token=refresh_token)

    refresh_token_key = settings.REFRESH_TOKEN_KEY_COOKIE
    response.delete_cookie(
        key=refresh_token_key,
        httponly=True,
        secure=True,
        samesite="none",
        path=BASE_URL+"/auth"
    )
    return AppResponse(
        message=f"🎉 Đăng xuất thành công.",
        data=None
    )

@router.get("/get-me", response_model=AppResponse[schemas_account.Response])
def getMe(
    current_account: Account = Depends(jwt_service.get_current_account)
):
    """
    - API trả về thông tin admin hiện tại.
    - Sử dụng get_current_account - (func giải mã jwt và tìm kiếm user theo user_id được lưu để tạo jwt token) để trả về thông tin admin hiện tại.
    - Trả về Data theo cấu trúc AppResponse
    """
    return AppResponse(
        data=current_account,
        message=f"🎉 Lấy thông tin Admin hiện tại thành công!"
    )

@router.post("/clean-token", response_model=AppResponse)
def clean_token(
    db: Session = Depends(connect_db),
    current_account: Account = Depends(jwt_service.get_current_account)
):
    logic_auth.clean_token(db=db)

    return AppResponse(
        message=f"🎉 Dọn dẹp các token hết hạn thành công.",
        data=None
    )


    