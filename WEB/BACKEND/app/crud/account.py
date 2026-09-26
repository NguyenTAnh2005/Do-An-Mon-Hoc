from fastapi import status
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.core import password
from app.models.models import Account
from app.schemas import account as schemas_account

from app.core.app_exception import AppException

def get_account(db: Session, target_id: int):
    """
    Func nhận vào là 1 id account
    Tìm kiếm account dựa theo biến id và trả về kết quả
    """
    db_account = db.query(Account).filter(Account.id == target_id).first()
    if not db_account:
        raise AppException(
            status_code = status.HTTP_404_NOT_FOUND,
            error_code="ACCOUNT_NOT_FOUND",
            message=f"❌ Account không tồn tại trong hệ thống!"
        )
    return db_account


def get_account_by_email(db: Session, email: EmailStr):
    """
    Fuct nhận vào là email bất kỳ
    Kiểm tra trong db có account thì trả về
    """
    db_account = db.query(Account).filter(Account.email == email).first()
    if not db_account:
        raise AppException(
            status_code = status.HTTP_404_NOT_FOUND,
            error_code="1 ACCOUNT_NOT_FOUND",
            message=f"❌ Account không tồn tại trong hệ thống!"
        )
    return db_account

def create_account(db: Session, create_data: schemas_account.Create):
    """
    Funct nhận vào là các trường dữ liệu của 1 account. 
    Tiến hành tạo account và trả về.
    """
    new_pass_hash = password.get_password_hash(create_data.password)
    new_account = Account(
        email = create_data.email,
        username = create_data.username,
        password_hash = new_pass_hash
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account