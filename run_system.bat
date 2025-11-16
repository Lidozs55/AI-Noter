@echo off
REM Windows 启动脚本

echo 🚀 启动 AI Noter 系统...

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 需要 Python 环境
    exit /b 1
)

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 📦 安装依赖...
pip install -r requirements.txt

REM 安装 pywin32 post-install
python Scripts/pywin32_postinstall.py -install

REM 启动系统
echo ▶️ 启动系统...
python main.py

pause
