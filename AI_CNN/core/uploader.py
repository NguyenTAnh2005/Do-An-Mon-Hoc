"""Upload classification images without blocking the camera loop."""

import queue
import threading
import uuid
import requests
from config import BACKEND_URL, LOCAL_IMAGE_DIR, AI_POST_IMAGE_KEY, BACKEND_URL, LOCAL_IMAGE_DIR
import time

# Chỉ thử lại khi 404 (tin MQTT chưa kịp tạo dòng log). Đơn vị: giây.
RETRY_DELAYS = (1, 2, 4)


class Uploader:
    def __init__(self):
        # shortcut: queued images live in memory until upload fails, persist before enqueue if crash recovery is required.
        self.queue = queue.Queue(maxsize=16)
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()


    def submit(self, log_id: str, image_bytes: bytes):
        uuid.UUID(log_id)
        try:
            self.queue.put_nowait((log_id, image_bytes))
        except queue.Full:
            self._save_local(log_id, image_bytes)


    def _post_image(self, log_id: str, image_bytes: bytes):
        url = f"{BACKEND_URL.rstrip('/')}/{log_id}/image"
        for delay in (0,) + RETRY_DELAYS:
            time.sleep(delay)
            response = requests.post(
                url,
                headers={"X-API-Key": AI_POST_IMAGE_KEY},
                files={"file": ("frame.jpg", image_bytes, "image/jpeg")},
                timeout=10,
            )
            if response.status_code == 404:
                continue
            if response.status_code == 409:
                print(f"[Uploader] {log_id} đã có ảnh, bỏ qua")
                return
            response.raise_for_status()
            return
        raise RuntimeError("log_id chưa có trong DB sau nhiều lần thử")


    def _run(self):
        while True:
            item = self.queue.get()
            try:
                if item is None:
                    return
                log_id, image_bytes = item
                try:
                    self._post_image(log_id=log_id, image_bytes=image_bytes)
                except Exception as error:
                    print(f"[Uploader] Upload failed {log_id}: {error}")
                    try:
                        self._save_local(log_id, image_bytes)
                    except OSError as save_error:
                        print(f"[Uploader] Local save failed {log_id}: {save_error}")
            finally:
                self.queue.task_done()


    def _save_local(self, log_id: str, image_bytes: bytes):
        folder = LOCAL_IMAGE_DIR / log_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "frame.jpg").write_bytes(image_bytes)
        (folder / "meta.txt").write_text(f"log_id={log_id}\n", encoding="utf-8")


    def close(self):
        self.queue.put(None)
        self.queue.join()
        self.thread.join()
