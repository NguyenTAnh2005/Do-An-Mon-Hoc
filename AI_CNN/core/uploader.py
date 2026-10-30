"""Upload classification images without blocking the camera loop."""

import queue
import threading
import uuid

import requests

from config import BACKEND_URL, LOCAL_IMAGE_DIR


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

    def _run(self):
        while True:
            item = self.queue.get()
            try:
                if item is None:
                    return
                log_id, image_bytes = item
                try:
                    response = requests.post(
                        BACKEND_URL,
                        data={"log_id": log_id},
                        files={"file": ("frame.jpg", image_bytes, "image/jpeg")},
                        timeout=10,
                    )
                    response.raise_for_status()
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
