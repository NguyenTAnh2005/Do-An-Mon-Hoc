# Mã hóa mật khẩu 
from passlib.context import CryptContext

# Cấu hình thuật toán bcrypt để băm pass 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_password_hash(password: str)-> str:
    """ Băm mật khẩu gốc thành chuỗi mã hóa để lưu vào DB. """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ So sánh mật khẩu người dùng nhập với mật khẩu đã băm trong DB. """
    return pwd_context.verify(plain_password, hashed_password)