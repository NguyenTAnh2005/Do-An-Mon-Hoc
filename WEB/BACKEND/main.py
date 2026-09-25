# Handling Error 
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exception import AppException

# CORS
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

# Import router 

app = FastAPI()

# =========== Cấu hình CORS =================================================================

# ========================================================================================

# Thêm Router các API vào 

# Endpoint giúp đóng gói Object được trả về là App Exception ( Từ 1 object --> JSON - ngôn ngữ giao tiếp chung giữa Front và Back)
@app.exception_handler(AppException)
async def app_exeption_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code = exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
            "data": None
        }
    )
# ===========================================================


@app.get("/")
def read_root():
    return{"message":f"👋  Welcome to Backend of Website Phân Loại Rác!"}
