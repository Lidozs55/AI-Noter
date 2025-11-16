"""
配置文件：集中管理系统配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    # 尝试获取脚本所在目录
    base_dir = Path(__file__).parent.absolute()
except (NameError, AttributeError):
    # 如果 __file__ 不可用，使用当前工作目录
    base_dir = Path.cwd()

# ==================== 后端配置 ====================
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5001
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# ==================== API 配置 ====================
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
DASHSCOPE_MODEL = 'qwen-plus'

# ==================== 数据存储配置 ====================
DATA_DIR = Path(os.getenv('DATA_DIR', base_dir / 'data'))
NOTES_DIR = DATA_DIR / 'notes'
INDEX_FILE = DATA_DIR / 'index.json'
CLIPBOARD_HISTORY_FILE = Path(os.getenv('CLIPBOARD_HISTORY_FILE', base_dir / 'clipboard_history.json'))

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
NOTES_DIR.mkdir(exist_ok=True)

# ==================== 前端配置 ====================
FRONTEND_URL = 'http://127.0.0.1:8000'
FRONTEND_FILE = Path(base_dir / 'index.html')

# ==================== 监听配置 ====================
CLIPBOARD_CHECK_INTERVAL = int(os.getenv('CLIPBOARD_CHECK_INTERVAL', 1))
CLIPBOARD_HISTORY_LIMIT = int(os.getenv('CLIPBOARD_HISTORY_LIMIT', 500))

# ==================== 日志配置 ====================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = Path(os.getenv('LOG_FILE', base_dir / 'logs/app.log'))

# 确保日志目录存在
LOG_FILE.parent.mkdir(exist_ok=True)
