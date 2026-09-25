@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Setup cau truc thu muc WEB BACKEND
echo ============================================

set ROOT=.
set BE=%ROOT%\BACKEND

REM ================= Thu muc =================
mkdir "%BE%\app\core"
mkdir "%BE%\app\models"
mkdir "%BE%\app\schemas"
mkdir "%BE%\app\crud"
mkdir "%BE%\app\services"
mkdir "%BE%\app\api\v1\endpoints"

REM ================= File goc =================
type nul > "%BE%\main.py"
type nul > "%BE%\requirements.txt"
type nul > "%BE%\.env"
type nul > "%BE%\README.md"

if not exist "%BE%\.gitignore" (
    echo __pycache__/> "%BE%\.gitignore"
    echo .env>> "%BE%\.gitignore"
    echo venv/>> "%BE%\.gitignore"
    echo .pytest_cache/>> "%BE%\.gitignore"
)

REM ================= app/ =================
type nul > "%BE%\app\__init__.py"
type nul > "%BE%\app\db_connection.py"

REM --- core: cau hinh, auth, mqtt, websocket, cloudinary ---
type nul > "%BE%\app\core\__init__.py"
type nul > "%BE%\app\core\config.py"
type nul > "%BE%\app\core\jwt.py"
type nul > "%BE%\app\core\refresh_token.py"
type nul > "%BE%\app\core\password.py"
type nul > "%BE%\app\core\mqtt_client.py"
type nul > "%BE%\app\core\websocket_manager.py"
type nul > "%BE%\app\core\api_key_auth.py"
type nul > "%BE%\app\core\cloudinary_config.py"

REM --- models ---
type nul > "%BE%\app\models\__init__.py"
type nul > "%BE%\app\models\user.py"
type nul > "%BE%\app\models\khu_vuc.py"
type nul > "%BE%\app\models\thung_rac.py"
type nul > "%BE%\app\models\lich_su_phan_loai.py"

REM --- schemas ---
type nul > "%BE%\app\schemas\__init__.py"
type nul > "%BE%\app\schemas\user.py"
type nul > "%BE%\app\schemas\token.py"
type nul > "%BE%\app\schemas\khu_vuc.py"
type nul > "%BE%\app\schemas\thung_rac.py"
type nul > "%BE%\app\schemas\lich_su_phan_loai.py"
type nul > "%BE%\app\schemas\thong_ke.py"

REM --- crud ---
type nul > "%BE%\app\crud\__init__.py"
type nul > "%BE%\app\crud\user.py"
type nul > "%BE%\app\crud\token.py"
type nul > "%BE%\app\crud\khu_vuc.py"
type nul > "%BE%\app\crud\thung_rac.py"
type nul > "%BE%\app\crud\lich_su_phan_loai.py"

REM --- services ---
type nul > "%BE%\app\services\__init__.py"
type nul > "%BE%\app\services\auth.py"
type nul > "%BE%\app\services\mqtt_service.py"
type nul > "%BE%\app\services\lich_su_phan_loai.py"
type nul > "%BE%\app\services\thong_ke.py"

REM --- api/v1/endpoints ---
type nul > "%BE%\app\api\__init__.py"
type nul > "%BE%\app\api\v1\__init__.py"
type nul > "%BE%\app\api\v1\endpoints\__init__.py"
type nul > "%BE%\app\api\v1\endpoints\auth.py"
type nul > "%BE%\app\api\v1\endpoints\websocket.py"
type nul > "%BE%\app\api\v1\endpoints\khu_vuc.py"
type nul > "%BE%\app\api\v1\endpoints\thung_rac.py"
type nul > "%BE%\app\api\v1\endpoints\lich_su_phan_loai.py"
type nul > "%BE%\app\api\v1\endpoints\thong_ke.py"

echo.
echo ============================================
echo   Da tao xong cau truc WEB\BACKEND
echo ============================================

pause