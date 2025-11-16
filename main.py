"""
主启动文件：一键启动整个系统
启动包括：Flask 后端、剪切板监听、Web UI
"""
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

try:
    # 尝试使用 __file__ 获取脚本路径
    script_dir = Path(__file__).parent.absolute()
except (NameError, AttributeError):
    # 如果 __file__ 不可用，使用 os.getcwd()
    script_dir = Path.cwd()

sys.path.insert(0, str(script_dir))

from app import app
from clipboard_monitor import ClipboardMonitor


class AINotesSystem:
    """集成系统管理器"""
    
    def __init__(self):
        self.backend_url = "http://127.0.0.1:5001"
        self.frontend_path = Path("./index.html")
        self.clipboard_monitor = ClipboardMonitor(self.backend_url)
        self.is_running = False
    
    def start_backend(self):
        """启动 Flask 后端服务"""
        print("\n" + "=" * 60)
        print("🚀 启动 Flask 后端服务")
        print("=" * 60)
        # Flask 会在主线程运行
        app.run(debug=False, port=5001, host='127.0.0.1', use_reloader=False)
    
    def start_clipboard_monitor(self):
        """启动剪切板监听"""
        print("\n" + "=" * 60)
        print("📋 启动剪切板监听")
        print("=" * 60)
        # 等待后端启动
        time.sleep(2)
        self.clipboard_monitor.start(interval=1.0)
    
    def start_web_ui(self):
        """打开 Web UI"""
        print("\n" + "=" * 60)
        print("🌐 打开 Web 界面")
        print("=" * 60)
        # 等待后端启动
        time.sleep(3)
        
        if self.frontend_path.exists():
            frontend_url = f"file://{self.frontend_path.absolute()}"
            print(f"📂 打开: {frontend_url}")
            webbrowser.open(frontend_url)
        else:
            print(f"⚠️  前端文件未找到: {self.frontend_path}")
    
    def run(self):
        """启动完整系统"""
        print("\n")
        print("   █████╗ ██╗   ██╗ ███╗   ██╗ ██████╗ ████████╗███████╗██╗")
        print("  ██╔══██╗██║   ██║████╗  ██║██╔═══██╗╚══██╔══╝██╔════╝██║")
        print("  ███████║██║   ██║██╔██╗ ██║██║   ██║   ██║   █████╗  ██║")
        print("  ██╔══██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██╔══╝  ╚═╝")
        print("  ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝   ██║   ███████╗██╗")
        print("  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝")
        print("\n               智能工作助手 - 开启高效知识管理\n")
        
        self.is_running = True
        
        # 在单独的线程中启动剪切板监听和 Web UI
        clipboard_thread = threading.Thread(target=self.start_clipboard_monitor, daemon=True)
        ui_thread = threading.Thread(target=self.start_web_ui, daemon=True)
        
        clipboard_thread.start()
        ui_thread.start()
        
        try:
            # 主线程运行 Flask
            self.start_backend()
        except KeyboardInterrupt:
            print("\n\n🛑 系统正在关闭...")
            self.clipboard_monitor.stop()
            self.is_running = False


if __name__ == '__main__':
    system = AINotesSystem()
    system.run()
