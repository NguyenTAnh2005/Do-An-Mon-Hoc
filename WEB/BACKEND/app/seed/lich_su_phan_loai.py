import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.models import LichSuPhanLoai, KhuVuc, LoaiRac, KetQuaXacNhan

SO_LUONG_MAU = 150
SO_NGAY_TRO_VE_TRUOC = 30


def seed_lich_su_phan_loai(db: Session):
    """Sinh ~150 row lịch sử phân loại giả, rải trong 30 ngày gần nhất.

    Mục đích: có đủ data để test FE (dashboard, danh sách, filter theo khu vực/loại rác/thời gian).
    Cần khu_vuc đã có id (db.flush() sau seed_khu_vuc trước khi gọi hàm này).
    """
    khu_vuc_ids = [k.id for k in db.query(KhuVuc.id).all()]
    if not khu_vuc_ids:
        print("⚠️ Chưa có khu_vuc nào, hãy seed_khu_vuc (và flush) trước.")
        return

    now = datetime.now(timezone.utc)
    loai_rac_list = list(LoaiRac)

    count = 0
    for _ in range(SO_LUONG_MAU):
        thoi_gian = now - timedelta(
            days=random.uniform(0, SO_NGAY_TRO_VE_TRUOC),
            seconds=random.randint(0, 86400),
        )
        loai_rac = random.choice(loai_rac_list)
        do_chac_chan = round(random.uniform(0.55, 0.99), 2)
        log_id = str(uuid.uuid4())

        # 15% chưa có ảnh — giả lập case đang chờ HTTP upload về (luồng ảnh tách kênh)
        co_anh = random.random() > 0.15

        # Xác nhận thủ công: đa số chưa xác nhận, còn lại chia phần lớn đúng / ít sai
        roll = random.random()
        if roll < 0.6:
            ket_qua = KetQuaXacNhan.CHUA_XAC_NHAN
        elif roll < 0.85:
            ket_qua = KetQuaXacNhan.DUNG
        else:
            ket_qua = KetQuaXacNhan.SAI

        db.add(
            LichSuPhanLoai(
                log_id=log_id,
                khu_vuc_id=random.choice(khu_vuc_ids),
                loai_rac_nhan_dien=loai_rac,
                do_chac_chan=do_chac_chan,
                url_anh=(
                    f"https://res.cloudinary.com/df5mtvzkn/image/upload/v1790302346/Phan_loai_rac/journey-18-09_tyh0kk.jpg"
                    if co_anh
                    else None
                ),
                cloudinary_public_id=f"seed_{log_id}" if co_anh else None,
                ket_qua_xac_nhan=ket_qua,
                thoi_gian=thoi_gian,
            )
        )
        count += 1

    print(f"✅ seed_lich_su_phan_loai sẵn sàng ({count} row)!")