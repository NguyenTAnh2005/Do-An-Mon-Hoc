from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime, timezone

from app.core.app_exception import AppException

from app.models.models import RefreshToken
from app.schemas import refresh_token as schemas_token

# Get theo token hash
def get_by_token(db:Session, token_hash: str):
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not db_token:
        # Thiết kế lỗi 401 trùng lặp bên hàm refresh thay vì 404 
        # hacker sẽ biết được token này có trong hệ thống hay không qua nhiều lần thử
        
        # raise AppException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     error_code="TOKEN_NOT_FOUND",
        #     message=f"❌ This Refresh Token does not exist in system. Please verify the ID and try again."
        # )
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_REFRESH_TOKEN",
            message=f"❌ Phiên đăng nhập không hợp lệ, vui lòng đăng nhập lại."
        )
    return db_token

# get list by user id
def get_all_by_user_id(
    db: Session, user_id: int,
    skip: int,
    limit: int,
    sort_by: str,
    order: str
):
    query = db.query(RefreshToken).filter(RefreshToken.user_id==user_id)
    sort_column = getattr(RefreshToken, sort_by, RefreshToken.created_at)

    if order == "desc": query=query.order_by(desc(sort_column))
    else: query=query.order_by(asc(sort_column))

    list_data = query.offset(skip).limit(limit).all()

    return list_data

# create by user_id
def create(db: Session, create_data: schemas_token.Create):
    new_token = RefreshToken(**create_data.model_dump())
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    return new_token

# update revoked (false --> true) bởi 1 db refresh token (row cụ thể đó). 
def update_revoked(db: Session, db_token: RefreshToken):
    """
    Khi tạo mới row refresh token ta cần đánh dấu không sử dụng (revoked=True)
    cho token cũ, vẫn lưu lại Db để tránh tình trạng hacker có refresh token cũ
    và yêu cầu tạo mới access_token.
    """
    db_token.revoked = True

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token

# update revoked toàn bộ token của 1 user_id khi phát hiện xâm nhập 
def update_all_revoked(db:Session, user_id: int):
    """
    Khi revoke = True thì có nghĩa nó đã được xác định 
    là không sử dụng rồi nhưng lại có nguồn khác gửi đến
    -> Chứng tỏ ai đó đang xâm nhập (Chủ hoặc hacker đang gửi request qua)
    -> Xử lý an toàn -> revoked toàn bộ token hiện có của user
    """
    query = db.query(RefreshToken).filter(RefreshToken.user_id == user_id)
    # Tôi chưa rành nhiều sql cũng như code dạng ntn , lúc thì all lúc thì ko
    query.update({RefreshToken.revoked: True}, synchronize_session='fetch')

    db.commit()

    return

    
# delete by expire
def clean(db: Session):
    """
    1 access_token chỉ sống 15 phút, 1 lần tạo mới kéo theo tạo mới 1 access_token mới.
    Kéo theo sẽ có khá nhiều row ở bảng này. Do đó, việc dọn dẹp là khá cần thiết. 
    Và chỉ dọn dẹp những token đã HẾT HẠN kể cả revoke=True hay False.
    token CÒN HẠN sẽ được để lại với mục đích đăng nhập hoặc chống xâm nhập trái phép. 
    """
    query = db.query(RefreshToken).filter(RefreshToken.expires_at < datetime.now(timezone.utc))
    # Này chép theo gemini chứ chưa hiểu lắm
    deleted_count = query.delete(synchronize_session='fetch')

    db.commit()
    
    return deleted_count


