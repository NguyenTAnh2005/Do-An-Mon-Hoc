from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.core.config import settings
from typing import Optional
from app.core import jwt as jwt_service
from app.db_connection import connect_db


BASE_URL = settings.BASE_API_URL
router = APIRouter(
    prefix= BASE_URL
)

def is_valid_token(token: Optional[str] = None) -> bool:
    """
        Gọi trực tiếp connect_db thay vì dùng Depends. 
        connect_db tự chạy tự đóng với HTTP chỉ xảy ra trong 1 tg ngắn, 
        với ws thì việc chạy duy trì lâu hơn với while True 
        nên nó gây bị tốn kết nối trong pool (max = 15)
        ==> tự làm thẳng: trả về db sau đó đóng kết nối ngay
        Vì chỉ cần xác định token hợp lệ hay không ở bước đầu. 
    """
    if not token:
        return False
    db_session = connect_db()
    db = next(db_session)
    try:
        return jwt_service.get_account_from_token(token=token, db=db) is not None
    finally:
        db_session.close()

@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket, token: Optional[str] = None):
    """
        + Route websocket nhận Websocket thay vì Request như REST
        + Lấy phần tử manager thông qua app.state
        + accept(): hoàn thành handshake: req HTTP xin nâng cấp, 
        server trả về status 101 Switching Protocols, chấp nhận chuyển HTTP sang WS
        + Kết nối được duy trì cho tới khi kết thúc hàm. 
        + recieve_text: chờ tin từ client và không chặn even loop. 
        + Nếu client đóng thì liền ném lỗi disconnect, kết thúc lặp while true 
        đồng thời, except pass lỗi vì đây là cách đóng bình thường. Nếu không bắt và pass 
        thì exception lan ra Uvicorn ghi log lỗi. 
        + finally đóng kết nối.
    """
    manager = websocket.app.state.manager
    await websocket.accept()
    # Bắt lỗi jwt token 
    if not is_valid_token(token=token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)