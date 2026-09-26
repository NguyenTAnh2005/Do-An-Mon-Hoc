from pydantic import BaseModel
from datetime import datetime

class Response(BaseModel):
    id: int
    account_id: int
    token_hash: str
    expires_at: datetime

    # Database tự lo mặc định nên khỏi cần ở đây
    # created_at: datetime
    # revoked: bool

    class Config:
        from_attributes = True


class Create(BaseModel):
    account_id: int
    token_hash: str
    expires_at: datetime