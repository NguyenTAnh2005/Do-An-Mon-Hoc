from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FRONTEND_URL: str
    DATABASE_URL: str
    #...
    BASE_API_URL:str

    # Mã key để thực thi JWT
    SECRET_KEY: str
    # Thời hạn tồn tại tối đa của một lần cấp JWT (15 phút)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3
    # Biến refresh token lưu trên Cookie
    REFRESH_TOKEN_KEY_COOKIE : str = "refresh_token"
    
    # Tài khoản Manager seed data
    ST_EMAIL:str
    ST_USERNAME: str
    ST_PASSWORD: str


    # Cloudinary Service

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = True

settings = Settings()