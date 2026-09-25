from sqlalchemy.orm import Session

from app.models.models import ThungRac, KhuVuc, LoaiRac

CHIEU_CAO_MAC_DINH_CM = 50.0

LOAI_RAC_SLUG = {
    LoaiRac.TAI_CHE: "taiche",
    LoaiRac.HUU_CO: "huuco",
    LoaiRac.VO_CO: "voco",
}


def seed_thung_rac(db: Session):
    """Mỗi khu vực có đủ 3 thùng: tái chế / hữu cơ / vô cơ.

    Cần khu_vuc đã có id (db.flush() sau seed_khu_vuc trước khi gọi hàm này).
    """
    khu_vuc_list = db.query(KhuVuc).order_by(KhuVuc.id).all()
    if not khu_vuc_list:
        print("⚠️ Chưa có khu_vuc nào, hãy seed_khu_vuc (và flush) trước.")
        return

    count = 0
    for khu_vuc in khu_vuc_list:
        khu_n = khu_vuc.mqtt_topic_phanloai.split("/")[1]  # "khu1", "khu2", ...
        for loai_rac, slug in LOAI_RAC_SLUG.items():
            topic = f"truong/{khu_n}/mucday/{slug}"
            existing = db.query(ThungRac).filter(ThungRac.mqtt_topic_mucday == topic).first()
            if existing:
                continue
            db.add(
                ThungRac(
                    khu_vuc_id=khu_vuc.id,
                    loai_rac=loai_rac,
                    mqtt_topic_mucday=topic,
                    chieu_cao_H_cm=CHIEU_CAO_MAC_DINH_CM,
                    phan_tram_day_hien_tai=0.0,
                )
            )
            count += 1
    print(f"✅ seed_thung_rac sẵn sàng ({count} thùng mới)!")