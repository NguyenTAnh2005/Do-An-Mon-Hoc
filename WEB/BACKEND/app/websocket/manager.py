# File websocket manager quản lý các kết nối websocket của server
# cấu hình tập set ( tránh trùng dữ liệu ) chứa các web socket đang mở
# method cần: 
#   - connect (thêm vào)
#   - disconnect(ngắt kết nối)
#   - broadcast(gửi thông tin cho từng websocket)

import logging
from fastapi import WebSocket

logger = logging.getLogger("WS_manager")

class ConnectionManager:
    def __init__(self):
        # Khởi tạo tập rỗng set chứa các connect ws
        self.active: set[WebSocket] = set()

    def connect(self, websocket: WebSocket):
        """
            Function xử lý thêm một ws vào danh sách
        """
        self.active.add(websocket)
        logger.info(f" [WS] +1 kết nối, hiện có {len(self.active)}")

    def disconnect(self, websocket: WebSocket):
        """
            Function xử lý xóa 1 ws khỏi ds hiện tại 
        """
        # Dùng discard để không báo lỗi nếu như phần tử cần xóa không tồn tại 
        # Remove thì có báo lỗi
        self.active.discard(websocket)
        logger.info(f"[WS] -1 kết nối, còn {len(self.active)}")

    async def broadcast(self, message: dict):
        """
            Func gửi từng thông tin cập nhật sang cho các ws tương ứng với đầu nhận là fe
        """
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                logger.exception(" [WS] gửi thất bại, gỡ kết nối")
                self.active.discard(ws)
        