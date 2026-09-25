from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import TaiKhoan
from app.core.password import get_password_hash 


def seed_tai_khoan(db: Session):
    """Tạo tài khoản quản lý đầu tiên, lấy username/password từ .env."""
    username = settings.ST_ADMIN_EMAIL
    password = settings.ST_ADMIN_PASSWORD

    if not username or not password:
        print("⚠️ Không tìm thấy ADMIN_USERNAME / ADMIN_PASSWORD trong .env, bỏ qua seed_tai_khoan!")
        return

    existing = db.query(TaiKhoan).filter(TaiKhoan.ten_dang_nhap == username).first()
    if existing:
        print(f"ℹ️ Tài khoản '{username}' đã tồn tại, bỏ qua.")
        return

    tai_khoan = TaiKhoan(
        ten_dang_nhap=username,
        mat_khau_hash=get_password_hash(password),
    )
    db.add(tai_khoan)
    print("✅ seed_tai_khoan sẵn sàng!")