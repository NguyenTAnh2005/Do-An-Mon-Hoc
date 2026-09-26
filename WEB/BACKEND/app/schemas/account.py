from pydantic import BaseModel, EmailStr

class Response(BaseModel):
    id: int
    username: str
    email: EmailStr
    # Dòng code giair quyết vấn đề giữa SQLAlchemy và Pydantic
    # Pydantic thì chỉ biết đọc dữ liệu dạng từ điển --> Data["email"]
    # SqlAlchemy thì luôn trả về một Object sau khi truy vấn --> Data.email
    # Dòng code này cho phép Pydantic được phép xử lý làm việc với Object 
    # thay vì chỉ biết làm việc với Dictionary như bản chất ban đầu! 
    class Config:
        from_attributes = True

class Create(BaseModel):
    username: str
    email: EmailStr
    password: str
