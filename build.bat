@echo off
setlocal

title Build Student Finance (PyInstaller onedir + Inno Setup)
cls

echo ==============================================================================
echo                      STUDENT FINANCE - BUILD SCRIPT
echo                 Developer: AlfandoXeon (https://alfandoxeon.freedev.app)
echo ==============================================================================
echo.

:: 1. Pindah ke direktori script ini
cd /d "%~dp0"

:: 2. Periksa Python
echo [1/5] Memeriksa instalasi Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan di PATH sistem!
    echo Silakan install Python 3.12+ dan pastikan opsi Add Python to PATH dicentang.
    pause
    exit /b 1
)
python --version

:: 3. Periksa PyInstaller dan Pillow
echo.
echo [2/5] Memeriksa dependensi build (PyInstaller dan Pillow)...
python -c "import PyInstaller, PIL" >nul 2>&1
if errorlevel 1 (
    echo [*] Menginstal PyInstaller dan Pillow...
    python -m pip install --upgrade pyinstaller pillow
    if errorlevel 1 (
        echo [ERROR] Gagal menginstal dependensi build!
        pause
        exit /b 1
    )
) else (
    echo [*] PyInstaller dan Pillow sudah terinstal.
)

:: 4. Generate icon .ico multi-resolusi jika belum ada
echo.
echo [3/5] Memeriksa icon aplikasi (.ico)...
if not exist "icon\app_icon.ico" (
    echo [*] Mengonversi icon\icon.png menjadi icon\app_icon.ico...
    python -c "from PIL import Image; img = Image.open('icon/icon.png'); img.save('icon/app_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])"
    if not exist "icon\app_icon.ico" (
        echo [WARNING] Gagal membuat app_icon.ico, build akan dilanjutkan tanpa custom ico.
    ) else (
        echo [*] Icon multi-resolusi berhasil dibuat.
    )
) else (
    echo [*] icon\app_icon.ico ditemukan.
)

:: 5. Bersihkan direktori build lama
echo.
echo [4/5] Membersihkan cache build lama...
if exist "build" rmdir /s /q "build"
if exist "dist\Student Finance" rmdir /s /q "dist\Student Finance"

:: 6. Jalankan PyInstaller mode ONEDIR
echo.
echo [5/5] Menjalankan PyInstaller (mode: --onedir)...
echo Command: pyinstaller --noconsole --onedir --name "Student Finance" --icon "icon/app_icon.ico" --add-data "icon;icon" --clean --noconfirm main.py
echo.

python -m PyInstaller --noconsole --onedir --name "Student Finance" --icon "icon/app_icon.ico" --add-data "icon;icon" --clean --noconfirm main.py

if errorlevel 1 (
    echo.
    echo ==============================================================================
    echo [ERROR] Proses kompilasi PyInstaller gagal!
    echo ==============================================================================
    pause
    exit /b 1
)

:: Salin folder icon ke root dist untuk redundansi akses lokal
if not exist "dist\Student Finance\icon" (
    mkdir "dist\Student Finance\icon"
    copy "icon\*" "dist\Student Finance\icon\" >nul 2>&1
)

echo.
echo ==============================================================================
echo [SUKSES] Program one-dir berhasil dibuat!
echo Lokasi folder: "%~dp0dist\Student Finance\"
echo File executable: "%~dp0dist\Student Finance\Student Finance.exe"
echo ==============================================================================
echo.

:: 7. Kompilasi Inno Setup jika compiler (ISCC.exe) tersedia
set "ISCC_PATH="
where iscc.exe >nul 2>&1
if not errorlevel 1 for /f "delims=" %%i in ('where iscc.exe') do set "ISCC_PATH=%%i"

if "%ISCC_PATH%"=="" if exist "%SystemDrive%\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%SystemDrive%\Program Files (x86)\Inno Setup 6\ISCC.exe"
if "%ISCC_PATH%"=="" if exist "%SystemDrive%\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%SystemDrive%\Program Files\Inno Setup 6\ISCC.exe"

if not "%ISCC_PATH%"=="" goto compile_installer
goto no_installer_compiler

:compile_installer
echo [INFO] Inno Setup Compiler ditemukan di: "%ISCC_PATH%"
echo Membuat paket installer Windows Setup (.exe)...
echo.
"%ISCC_PATH%" "setup.iss"
if errorlevel 1 (
    echo [WARNING] Gagal mengompilasi setup.iss dengan ISCC.
) else (
    echo.
    echo ==============================================================================
    echo [SUKSES] Installer berhasil dibuat di folder: "%~dp0dist_installer\"
    echo ==============================================================================
)
goto finish

:no_installer_compiler
echo ------------------------------------------------------------------------------
echo [PETUNJUK MEMBUAT SETUP INSTALLER]
echo Inno Setup Compiler (ISCC.exe) belum terinstal pada PATH default.
echo.
echo Untuk membuat file Setup Installer (.exe):
echo 1. Unduh dan install Inno Setup 6 (gratis) dari: https://jrsoftware.org/isdl.php
echo 2. Buka file "setup.iss" di folder ini dengan Inno Setup Compiler.
echo 3. Tekan Ctrl+F9 (atau menu Build -> Compile).
echo 4. File installer (.exe) akan otomatis dibuat di folder "dist_installer\".
echo ------------------------------------------------------------------------------
goto finish

:finish
echo.
pause
