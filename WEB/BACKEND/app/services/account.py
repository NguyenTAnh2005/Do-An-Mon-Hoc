from sqlalchemy.orm import Session
from fastapi import status
from app.core.config import settings

from app.core.app_exception import AppException
from app.core import password 

from app.schemas import account as schemas_account
from app.crud import account as crud_account
from app.models.models import Account

def create_account(db: Session, create_data:schemas_account.Create):
    """
    Logic tạo một tk account.
    Check xem có email và username đang tạo đã tồn tại trong DB hay chưa. 
    Nếu chưa thì gọi tạo. 
    """
    db_account = db.query(Account).filter(
        (Account.email == create_data.email)|(Account.username == create_data.username)
        ).first()
    if db_account:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            error_code="ACCOUNT_AVAILABLE",
            message=f"❌ Đã tồn tại Account trùng email hoặc username trong hệ thống!"
        )
    new_account = crud_account.create_account(db=db, create_data=create_data)
    return new_account

