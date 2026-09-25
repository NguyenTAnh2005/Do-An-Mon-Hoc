from app.db_connection import SessionLocal  # TODO: đổi theo đúng path SessionLocal của dự án

from app.seed.tai_khoan import seed_tai_khoan
from app.seed.khu_vuc import seed_khu_vuc
from app.seed.thung_rac import seed_thung_rac
from app.seed.lich_su_phan_loai import seed_lich_su_phan_loai


def run_seed():
    db = SessionLocal()
    print("📢 Bắt đầu seed data ...........")
    try:
        seed_tai_khoan(db)
        seed_khu_vuc(db)
        db.flush()  # cần id của khu_vuc để gán FK cho thung_rac / lich_su_phan_loai bên dưới

        seed_thung_rac(db)
        seed_lich_su_phan_loai(db)

        db.commit()
        print("✅ Seed data thành công, đã commit toàn bộ!")
    except Exception as e:
        db.rollback()
        print(f"❌ Oops, lỗi khi seed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()