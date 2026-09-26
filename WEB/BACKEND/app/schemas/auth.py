from typing import Optional
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str


class TokenPayload(BaseModel):
    data: Optional[int] = None  # Chứa id tài khoản
    sub: Optional[str] = None   # Chứa Email tài khoản