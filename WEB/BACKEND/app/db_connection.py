from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Find DB Url 
# (Load đường dẫn lưu trữ database từ pydantic setting)
DATABASE_URL=settings.DATABASE_URL

# Create Engine that connect to Database 
# (Tạo Engine - kết nối đến database - mọi truy cập đến database đều thông qua thằng này)
engine = create_engine(DATABASE_URL)

# Crate Sesion Maker - provide session to connect to database 
# (Tạo phiên làm việc khi kết nối đến database )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function connection to database 
# (Hàm lấy phiên làm việc và kết nối với database thông qua máy tạo session và kết nối database - engine)
def connect_db():
    """
    Tạo phiên từ Session Local và chạy tới database để làm việc,
    xong việc tự đóng kết nối tránh việc app quá tải thông qua lệnh yield
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()