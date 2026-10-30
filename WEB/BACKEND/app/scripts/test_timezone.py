from sqlalchemy import Date, cast, func, select, text

from app.db_connection import SessionLocal  # <-- sửa cho đúng đường dẫn của bạn
from app.models.models import ClassificationLog

from datetime import timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))

# Mốc cố định: 23:00 UTC ngày 26/10 = 06:00 giờ VN ngày 27/10
FIXED_UTC = "2026-10-26 23:00:00+00"


def test_fixed_timestamp(db):
    print("=== Phần 1: mốc cố định 23:00 UTC ngày 26/10 ===")
    print("Kỳ vọng: ngày giờ VN phải là 2026-10-27 dù phiên đặt múi giờ nào\n")

    for session_tz in ["UTC", "Asia/Ho_Chi_Minh"]:
        db.execute(text(f"SET TIME ZONE '{session_tz}'"))

        # Cách cũ: ép thẳng sang date, phụ thuộc múi giờ của phiên
        naive_date = db.execute(
            text(f"SELECT CAST(TIMESTAMPTZ '{FIXED_UTC}' AS date)")
        ).scalar_one()

        # Cách mới: đổi sang giờ VN trước rồi mới lấy ngày
        vn_date = db.execute(
            text(
                f"SELECT CAST(timezone('Asia/Ho_Chi_Minh', "
                f"TIMESTAMPTZ '{FIXED_UTC}') AS date)"
            )
        ).scalar_one()

        print(f"Phiên đặt {session_tz:<17} | ép thẳng: {naive_date} | dùng timezone(): {vn_date}")
        assert str(vn_date) == "2026-10-27", "timezone() trả sai ngày!"

    print("\nOK: timezone() luôn ra 2026-10-27, còn cách ép thẳng thì đổi theo phiên.\n")


def test_real_data(db):
    print("=== Phần 2: dữ liệu thật trong classification_log ===")
    vn_time = func.timezone("Asia/Ho_Chi_Minh", ClassificationLog.created_at)

    query = (
        select(
            ClassificationLog.created_at,
            vn_time.label("vn_time"),
            cast(vn_time, Date).label("vn_date"),
        )
        .order_by(ClassificationLog.created_at.desc())
        .limit(5)
    )

    rows = db.execute(query).all()
    if not rows:
        print("Bảng chưa có dữ liệu.")
        return

    for created_at, vn_time_value, vn_date in rows:
        print(f"created_at: {created_at} | giờ VN: {vn_time_value} | ngày VN: {vn_date}")

    # Kiểm tra: giờ VN phải bằng created_at (đã đổi sang +07) bỏ múi giờ
    for created_at, vn_time_value, vn_date in rows:
        expected = created_at.astimezone(VN_TZ).replace(tzinfo=None)
        assert vn_time_value == expected, f"Lệch giờ: {vn_time_value} != {expected}"
        assert vn_date == expected.date(), f"Lệch ngày: {vn_date} != {expected.date()}"

    print("\nOK: giờ VN và ngày VN từ SQL khớp với phép đổi của Python.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        test_fixed_timestamp(db)
        test_real_data(db)
    finally:
        db.close()