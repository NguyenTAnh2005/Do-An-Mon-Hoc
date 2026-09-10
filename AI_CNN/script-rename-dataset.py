import os

# Thư mục gốc chứa script (AI_CNN) và thư mục dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "data")

SPLITS = ['train', 'test', 'valid']

def rename_and_count(root_dir, splits):
    stats = {}
    
    for split in splits:
        images_dir = os.path.join(root_dir, split, 'images')
        labels_dir = os.path.join(root_dir, split, 'labels')

        if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
            print(f"⚠️ Bỏ qua tập '{split}': Không tìm thấy folder 'images' hoặc 'labels'.")
            stats[split] = 0
            continue

        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        image_files.sort()

        print(f"🔄 Đang xử lý tập '{split}'... Tìm thấy {len(image_files)} ảnh.")
        success_count = 0

        for index, old_img_name in enumerate(image_files, start=1):
            new_base_name = f"{split}_{index}"
            img_ext = os.path.splitext(old_img_name)[1]
            
            new_img_name = f"{new_base_name}{img_ext}"
            new_lbl_name = f"{new_base_name}.txt"

            old_img_path = os.path.join(images_dir, old_img_name)
            new_img_path = os.path.join(images_dir, new_img_name)

            old_lbl_name = os.path.splitext(old_img_name)[0] + ".txt"
            old_lbl_path = os.path.join(labels_dir, old_lbl_name)
            new_lbl_path = os.path.join(labels_dir, new_lbl_name)

            # Chỉ đổi tên nếu tồn tại cả ảnh và label
            if os.path.exists(old_lbl_path):
                try:
                    os.rename(old_lbl_path, new_lbl_path)
                    os.rename(old_img_path, new_img_path)
                    success_count += 1
                except Exception as e:
                    print(f"❌ Lỗi khi đổi tên {old_img_name}: {e}")
            else:
                print(f"⚠️ Cảnh báo: Ảnh '{old_img_name}' thiếu file label. Đã bỏ qua.")
        
        stats[split] = success_count

    # In thống kê
    print("\n📊 THỐNG KÊ SỐ LƯỢNG DATASET SAU KHI XỬ LÝ:")
    total = 0
    for split, count in stats.items():
        print(f" - Tập {split}: {count} file hợp lệ")
        total += count
    print(f" => TỔNG CỘNG: {total} file.")
    print("✅ Hoàn tất chuẩn hóa tên Dataset!")

if __name__ == "__main__":
    rename_and_count(DATASET_DIR, SPLITS)