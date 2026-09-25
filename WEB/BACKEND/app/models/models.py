import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# ================================
# Enum
# ================================
class LoaiRac(str, enum.Enum):
    """Phân loại 3 loại rác — dùng cho cả thung_rac và lich_su_phan_loai."""
    TAI_CHE = "tai_che"
    HUU_CO = "huu_co"
    VO_CO = "vo_co"


class KetQuaXacNhan(str, enum.Enum):
    """Trạng thái xác nhận thủ công của quản lý cho 1 lượt nhận diện."""
    CHUA_XAC_NHAN = "chua_xac_nhan"
    DUNG = "dung"
    SAI = "sai"


# ================================
# 1. Bảng Tài khoản
# ================================
class TaiKhoan(Base):
    __tablename__ = "tai_khoan"

    id: Mapped[int] = mapped_column(primary_key=True)
    ten_dang_nhap: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    mat_khau_hash: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship
    refresh_token: Mapped[list["RefreshToken"]] = relationship(back_populates="tai_khoan")


# ================================
# 2. Bảng Khu vực
# ================================
class KhuVuc(Base):
    __tablename__ = "khu_vuc"

    id: Mapped[int] = mapped_column(primary_key=True)
    mo_ta_vi_tri: Mapped[str] = mapped_column(String(255), nullable=False)

    # Full MQTT topic riêng cho từng khu vực — không nối chuỗi prefix (đã chốt)
    mqtt_topic_phanloai: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    mqtt_topic_trangthai_iot: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    mqtt_topic_trangthai_ai: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Trạng thái online tách riêng IoT / AI, cập nhật qua LWT
    iot_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    iot_lan_cuoi_online: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_lan_cuoi_online: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    thung_rac: Mapped[list["ThungRac"]] = relationship(back_populates="khu_vuc")
    lich_su_phan_loai: Mapped[list["LichSuPhanLoai"]] = relationship(back_populates="khu_vuc")


# ================================
# 3. Bảng Thùng rác
# ================================
class ThungRac(Base):
    __tablename__ = "thung_rac"

    id: Mapped[int] = mapped_column(primary_key=True)
    khu_vuc_id: Mapped[int] = mapped_column(ForeignKey("khu_vuc.id"), nullable=False, index=True)

    loai_rac: Mapped[LoaiRac] = mapped_column(SQLEnum(LoaiRac, name="loai_rac_enum"), nullable=False)

    # Full MQTT topic riêng của từng thùng, vd: truong/khu1/mucday/huuco
    mqtt_topic_mucday: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    chieu_cao_H_cm: Mapped[float] = mapped_column(Float, nullable=False)
    # % đầy = (H - d) / H * 100, ghi đè liên tục — KHÔNG lưu lịch sử theo thời gian (đã chốt)
    phan_tram_day_hien_tai: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cap_nhat_luc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    khu_vuc: Mapped["KhuVuc"] = relationship(back_populates="thung_rac")


# ================================
# 4. Bảng Lịch sử phân loại
# ================================
class LichSuPhanLoai(Base):
    __tablename__ = "lich_su_phan_loai"

    # PK tự tăng dùng để join/hiển thị/phân trang bình thường
    id: Mapped[int] = mapped_column(primary_key=True)

    # UUID do script AI tự sinh, chỉ dùng để ghép nối MQTT + ảnh (KHÔNG dùng làm PK)
    log_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)

    khu_vuc_id: Mapped[int] = mapped_column(ForeignKey("khu_vuc.id"), nullable=False, index=True)

    loai_rac_nhan_dien: Mapped[LoaiRac] = mapped_column(SQLEnum(LoaiRac, name="loai_rac_enum"), nullable=False)
    do_chac_chan: Mapped[float] = mapped_column(Float, nullable=False)

    # NULL tạm tới khi ảnh HTTP (multipart) về, Backend update theo log_id (luồng ảnh tách kênh)
    url_anh: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cloudinary_public_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    ket_qua_xac_nhan: Mapped[KetQuaXacNhan] = mapped_column(
        SQLEnum(KetQuaXacNhan, name="ket_qua_xac_nhan_enum"),
        default=KetQuaXacNhan.CHUA_XAC_NHAN,
        nullable=False,
    )

    thoi_gian: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship
    khu_vuc: Mapped["KhuVuc"] = relationship(back_populates="lich_su_phan_loai")


# ================================
# 5. Bảng Refresh Token
# ================================
class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    tai_khoan_id: Mapped[int] = mapped_column(
        ForeignKey("tai_khoan.id", ondelete="CASCADE"), index=True, nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship
    tai_khoan: Mapped["TaiKhoan"] = relationship(back_populates="refresh_token")