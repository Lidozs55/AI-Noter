import time
import json
import threading
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import win32clipboard
    import win32con
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("⚠️  win32clipboard not available. Using fallback method.")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    print("⚠️  pyperclip not available.")


class ClipboardMonitor:
    """
    监听系统剪切板，自动捕获复制的内容
    支持文本、图片、链接等多种格式
    """
    
    def __init__(self, backend_url: str = "http://127.0.0.1:5001"):
        self.backend_url = backend_url
        self.last_clipboard_content = None
        self.monitoring = False
        self.captured_items = []
        try:
            base_dir = Path(__file__).parent.absolute()
        except (NameError, AttributeError):
            base_dir = Path.cwd()
        self.history_file = base_dir / 'clipboard_history.json'
        self.load_history()
    
    def load_history(self):
        """加载剪切板历史"""
        try:
            if self.history_file.exists():
                self.captured_items = json.loads(self.history_file.read_text(encoding='utf-8'))
        except:
            self.captured_items = []
    
    def save_history(self):
        """保存剪切板历史"""
        try:
            self.history_file.write_text(
                json.dumps(self.captured_items, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"❌ Failed to save history: {e}")
    
    def get_clipboard_content_windows(self) -> Optional[Dict[str, Any]]:
        """
        Windows 系统：使用 win32clipboard 获取剪切板内容
        支持文本和图片
        """
        if not WINDOWS_AVAILABLE:
            return None
        
        try:
            win32clipboard.OpenClipboard()
            
            result = {'type': 'text', 'content': None, 'formats': []}
            
            # 尝试获取文本
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                result['formats'].append('text')
                try:
                    text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    result['content'] = text
                    result['type'] = 'text'
                except:
                    pass
            
            # 尝试获取 HTML
            try:
                cf_html = win32con.CF_HTML
                if win32clipboard.IsClipboardFormatAvailable(cf_html):
                    result['formats'].append('html')
            except AttributeError:
                pass
            
            # 尝试获取文件列表
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                    result['formats'].append('files')
                    files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                    result['files'] = files
                    result['type'] = 'files'
            except:
                pass
            
            win32clipboard.CloseClipboard()
            
            if result['content'] or result.get('files'):
                return result
            
        except Exception as e:
            print(f"❌ Windows clipboard error: {e}")
        
        return None
    
    def get_clipboard_content_fallback(self) -> Optional[Dict[str, Any]]:
        """
        备用方案：使用 pyperclip 或 xclip 获取文本
        """
        try:
            if PYPERCLIP_AVAILABLE:
                text = pyperclip.paste()
                if text:
                    return {'type': 'text', 'content': text, 'formats': ['text']}
        except:
            pass
        
        return None
    
    def get_clipboard_content(self) -> Optional[Dict[str, Any]]:
        """获取剪切板内容（主方法）"""
        # 优先使用 Windows API
        if WINDOWS_AVAILABLE:
            content = self.get_clipboard_content_windows()
            if content:
                return content
        
        # 回退到 pyperclip
        return self.get_clipboard_content_fallback()
    
    def extract_urls(self, text: str) -> list:
        """从文本中提取 URL"""
        import re
        url_pattern = r'https?://[^\s]+'
        return re.findall(url_pattern, text)
    
    def send_to_backend(self, content: Dict[str, Any]) -> bool:
        """将剪切板内容发送到后端"""
        try:
            # 提取纯文本
            text_content = content.get('content', '')
            if not text_content:
                return False
            
            # 检查是否是 URL
            urls = self.extract_urls(text_content)
            
            payload = {
                'content': text_content,
                'type': content.get('type'),
                'urls': urls,
                'timestamp': datetime.now().isoformat(),
                'source': 'clipboard_monitor'
            }
            
            # 发送到后端
            response = requests.post(
                f"{self.backend_url}/api/classify-content",
                json={'content': text_content},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                payload['ai_classification'] = result
                
                # 记录到历史
                self.captured_items.append(payload)
                self.save_history()
                
                return True
            else:
                print(f"⚠️  Backend returned: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Failed to send to backend: {e}")
            return False
    
    def monitor_loop(self, interval: float = 1.0):
        """
        主监听循环
        每隔 interval 秒检查一次剪切板
        """
        print(f"▶️  Starting clipboard monitor (interval: {interval}s)")
        
        while self.monitoring:
            try:
                clipboard_content = self.get_clipboard_content()
                
                if clipboard_content:
                    current_content = clipboard_content.get('content')
                    
                    # 检测到新内容
                    if current_content and current_content != self.last_clipboard_content:
                        print(f"\n📋 New clipboard content detected!")
                        print(f"   Type: {clipboard_content.get('type')}")
                        print(f"   Preview: {current_content[:100]}...")
                        
                        # 发送到后端进行 AI 分类
                        if self.send_to_backend(clipboard_content):
                            print(f"✅ Content sent to backend for classification")
                        
                        self.last_clipboard_content = current_content
                
                time.sleep(interval)
            
            except Exception as e:
                print(f"❌ Monitor loop error: {e}")
                time.sleep(interval)
    
    def start(self, interval: float = 1.0):
        """启动监听线程"""
        if self.monitoring:
            print("⚠️  Monitor already running")
            return
        
        self.monitoring = True
        thread = threading.Thread(target=self.monitor_loop, args=(interval,), daemon=True)
        thread.start()
        print("✅ Clipboard monitor started")
    
    def stop(self):
        """停止监听"""
        self.monitoring = False
        print("⏹️  Clipboard monitor stopped")
    
    def get_history(self, limit: int = 50) -> list:
        """获取捕获历史"""
        return self.captured_items[-limit:]
    
    def clear_history(self):
        """清空历史"""
        self.captured_items = []
        self.save_history()


class ManualContentCapture:
    """
    手动内容捕获：支持文本输入、文件拖拽、URL 输入
    """
    
    def __init__(self, backend_url: str = "http://127.0.0.1:5001"):
        self.backend_url = backend_url
    
    def capture_text(self, text: str) -> Dict[str, Any]:
        """手动输入文本"""
        return {
            'type': 'text',
            'content': text,
            'source': 'manual_input',
            'timestamp': datetime.now().isoformat()
        }
    
    def capture_file(self, file_path: str) -> Dict[str, Any]:
        """读取文件内容"""
        try:
            path = Path(file_path)
            
            if path.suffix.lower() in ['.txt', '.md', '.json', '.py', '.js', '.java']:
                # 文本文件
                content = path.read_text(encoding='utf-8')
                return {
                    'type': 'text',
                    'content': content,
                    'source': 'file_upload',
                    'filename': path.name,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # 二进制文件
                return {
                    'type': 'file',
                    'filename': path.name,
                    'size': path.stat().st_size,
                    'source': 'file_upload',
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            return {'error': str(e), 'source': 'file_upload'}
    
    def capture_url(self, url: str) -> Dict[str, Any]:
        """捕获 URL（后续可集成网页内容爬取）"""
        return {
            'type': 'url',
            'content': url,
            'source': 'manual_input',
            'timestamp': datetime.now().isoformat()
        }
    
    def send_to_backend(self, content: Dict[str, Any]) -> bool:
        """发送到后端"""
        try:
            text_content = content.get('content', '')
            if not text_content:
                return False
            
            response = requests.post(
                f"{self.backend_url}/api/classify-content",
                json={'content': text_content},
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            print(f"❌ Failed to send to backend: {e}")
            return False


# ==================== 使用示例 ====================

if __name__ == '__main__':
    # 创建监听器
    monitor = ClipboardMonitor()
    
    # 启动监听（后台线程）
    monitor.start(interval=1.0)
    
    print("📝 Clipboard monitor is running. Copy something to trigger...")
    print("Press Ctrl+C to stop.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping monitor...")
        monitor.stop()
        print("✅ Monitor stopped")
