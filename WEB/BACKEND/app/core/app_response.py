from typing import Optional, Generic, TypeVar
from pydantic import BaseModel


# RESPONSE NẾU THÀNH CÔNG
# Tạo biến T là kiểu dữ liệu động (Generic Type)
T = TypeVar("T")
class AppResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None