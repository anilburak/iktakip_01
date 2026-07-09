@echo off
setlocal

set "APP_NAME=Personel_Takip_Sistemi"

where pyinstaller >nul 2>nul
if %ERRORLEVEL%==0 (
  pyinstaller --noconfirm --onedir --windowed --name "%APP_NAME%" --collect-all PIL --collect-all reportlab --collect-all openpyxl --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageDraw --hidden-import PIL.ImageFont --hidden-import reportlab --hidden-import reportlab.platypus --hidden-import openpyxl ik_takip.py
) else (
  python -m PyInstaller --noconfirm --onedir --windowed --name "%APP_NAME%" --collect-all PIL --collect-all reportlab --collect-all openpyxl --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageDraw --hidden-import PIL.ImageFont --hidden-import reportlab --hidden-import reportlab.platypus --hidden-import openpyxl ik_takip.py
)

if not exist "dist\%APP_NAME%\config.json" copy "config.json" "dist\%APP_NAME%\config.json"

echo.
echo Exe hazir: dist\%APP_NAME%\%APP_NAME%.exe
echo config.json exe klasorunun disinda, ayni klasorde tutulur.
pause
