@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Setup cau truc thu muc WEB Frontend
echo   (chay npm create vite truoc file nay)
echo ============================================

set ROOT=.
set FE=%ROOT%\FRONTEND

REM ================= Thu muc =================
mkdir "%FE%\src\contexts"
mkdir "%FE%\src\hooks"
mkdir "%FE%\src\routes"
mkdir "%FE%\src\pages"
mkdir "%FE%\src\layout"
mkdir "%FE%\src\components\ui"
mkdir "%FE%\src\components\wrapper"
mkdir "%FE%\src\service\config"
mkdir "%FE%\src\utils"

REM ================= File goc =================
type nul > "%FE%\.env"

if not exist "%FE%\.gitignore" (
    echo node_modules/> "%FE%\.gitignore"
    echo dist/>> "%FE%\.gitignore"
    echo .env>> "%FE%\.gitignore"
)

REM App.jsx va main.jsx da duoc vite tao san, KHONG dong den de khong ghi de

REM --- contexts ---
type nul > "%FE%\src\contexts\AuthContext.jsx"
type nul > "%FE%\src\contexts\WebSocketContext.jsx"

REM --- hooks ---
type nul > "%FE%\src\hooks\useAuth.js"
type nul > "%FE%\src\hooks\useWebSocket.js"

REM --- routes ---
type nul > "%FE%\src\routes\AuthProtected.jsx"
type nul > "%FE%\src\routes\AppRoute.jsx"

REM --- pages ---
type nul > "%FE%\src\pages\Login.jsx"
type nul > "%FE%\src\pages\Dashboard.jsx"
type nul > "%FE%\src\pages\QuanLyLichSu.jsx"
type nul > "%FE%\src\pages\ThongKe.jsx"

REM --- layout ---
type nul > "%FE%\src\layout\Layout.jsx"

REM --- components ---
type nul > "%FE%\src\components\ThungRacCard.jsx"
type nul > "%FE%\src\components\KhuVucStatus.jsx"
type nul > "%FE%\src\components\LichSuPhanLoaiItem.jsx"

type nul > "%FE%\src\components\ui\Input.jsx"
type nul > "%FE%\src\components\ui\Pagination.jsx"
type nul > "%FE%\src\components\ui\ThemeToggle.jsx"
type nul > "%FE%\src\components\ui\FetchStatus.jsx"

type nul > "%FE%\src\components\wrapper\Button.jsx"
type nul > "%FE%\src\components\wrapper\Modal.jsx"
type nul > "%FE%\src\components\wrapper\CardItem.jsx"

REM --- service (goi API + websocket) ---
type nul > "%FE%\src\service\config\autoConfig.js"
type nul > "%FE%\src\service\config\manualConfig.js"
type nul > "%FE%\src\service\auth.js"
type nul > "%FE%\src\service\khuVuc.js"
type nul > "%FE%\src\service\thungRac.js"
type nul > "%FE%\src\service\lichSuPhanLoai.js"
type nul > "%FE%\src\service\thongKe.js"
type nul > "%FE%\src\service\websocket.js"

REM --- utils ---
type nul > "%FE%\src\utils\axiosHelper.js"
type nul > "%FE%\src\utils\dateISO.js"
type nul > "%FE%\src\utils\string.js"

echo.
echo ============================================
echo   Da tao xong cau truc WEB\frontend
echo ============================================

pause