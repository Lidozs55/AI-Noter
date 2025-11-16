"""
安装系统依赖脚本
用于 Windows 平台上安装 win32clipboard
"""
import subprocess
import sys

def install_windows_dependencies():
    """安装 Windows 专用依赖"""
    packages = [
        'pywin32',
        'pyperclip',
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("\n✅ All dependencies installed!")
    print("\n📌 Post-installation for pywin32:")
    print("   Run: python Scripts/pywin32_postinstall.py -install")


if __name__ == '__main__':
    import platform
    
    if platform.system() == 'Windows':
        install_windows_dependencies()
    else:
        print("⚠️  This script is for Windows platform.")
        print("For Linux/Mac, install: pip install pyperclip")
