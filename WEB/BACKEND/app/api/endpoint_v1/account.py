from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db_connection import connect_db
from app.core.app_response import AppResponse
from app.core import jwt as jwt_service
from app.models.models import Account

from app.schemas import account as schemas_account
from app.crud import account as crud_account
from app.services import account as logic_account

BASE_URL = settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/accoount",
    tags=["Account"]
)

@router.post("/", response_model=AppResponse[schemas_account.Response])
def create_account(
    create_data: schemas_account.Create,
    db: Session = Depends(connect_db), 
    current_account: Account = Depends(jwt_service.get_current_account) 
):
    """
    ## API tạo mới Account
        + Đầu vào là JSON theo cấu trúc class Pydantic
        + Gọi hàm logic 
        + --> Trả về object đã tạo được
    """

    result = logic_account.create_account(db=db, create_data=create_data)
    
    return AppResponse(
        message=f"🎉 Tạo tài khoản thành công.",
        data=result
    )
    
@router.get("/{account_id}", response_model=AppResponse[schemas_account.Response])
def get_account(
    account_id: int, 
    db: Session = Depends(connect_db),
    current_account: Account = Depends(jwt_service.get_current_account) 
):
    """
    ## API lấy thông tin Account với id
        + Nhận id account và trả về kết quả tương ứng từ func bên crud.
        + Trả về kết quả dưới dạng ResponseModel
    """
    result = crud_account.get_account(db=db, target_id=account_id)
    return AppResponse(
        message=f"🎉 Tìm thấy Account.",
        data= result
    )


