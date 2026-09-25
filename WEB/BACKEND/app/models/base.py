from sqlalchemy.orm import DeclarativeBase

# Create Base Class for ORM models 
# (Tạo lớp cơ sở cho các mô hình ORM để dựa vào nó tạo ra các bảng trong database thật)
class Base(DeclarativeBase):
    """Base class dùng chung cho toàn bộ model trong dự án."""
    pass