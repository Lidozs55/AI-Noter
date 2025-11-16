# 剪切板监听与内容捕获

## 功能说明

### 1. 自动剪切板监听（Windows）
- 使用 `win32clipboard` 库监听系统剪切板
- 自动检测新复制的内容
- 支持文本、HTML、文件等格式
- 后台线程运行，不阻塞主程序

### 2. 手动内容捕获
- 文本直接输入
- 文件拖拽上传
- URL 链接捕获
- 支持批量处理

## 安装与配置

### Windows 用户

\`\`\`bash
# 安装依赖
pip install pywin32 pyperclip

# 如需 post-install 处理
python Scripts/pywin32_postinstall.py -install
\`\`\`

### Linux/Mac 用户

\`\`\`bash
# 安装 pyperclip（基础支持）
pip install pyperclip
\`\`\`

## 使用示例

### 启动自动监听

\`\`\`python
from clipboard_monitor import ClipboardMonitor

monitor = ClipboardMonitor(backend_url="http://127.0.0.1:5001")
monitor.start(interval=1.0)  # 每秒检查一次

# 查看历史
print(monitor.get_history())

# 停止监听
monitor.stop()
\`\`\`

### 手动捕获

\`\`\`python
from clipboard_monitor import ManualContentCapture

capture = ManualContentCapture()

# 文本输入
content = capture.capture_text("My notes here")
capture.send_to_backend(content)

# 文件上传
content = capture.capture_file("path/to/file.txt")

# URL 捕获
content = capture.capture_url("https://example.com")
\`\`\`

## 数据流程

\`\`\`
剪切板内容
    ↓
监听检测
    ↓
提取文本/URL
    ↓
发送到后端 API
    ↓
AI 分类与整理
    ↓
保存到本地文件 + 索引
\`\`\`

## 剪切板历史记录

所有捕获的内容自动保存到 `clipboard_history.json`：

\`\`\`json
[
  {
    "type": "text",
    "content": "captured content here",
    "urls": [],
    "timestamp": "2024-01-15T12:00:00",
    "source": "clipboard_monitor",
    "ai_classification": {
      "is_note": true,
      "note_type": "零散知识"
    }
  }
]
\`\`\`

## 故障排查

**Q: Windows 上 win32clipboard 不工作**
A: 运行 `python Scripts/pywin32_postinstall.py -install`

**Q: 监听不到新内容**
A: 确保复制内容后至少等待 1 秒（默认检查间隔）

**Q: 内存占用过高**
A: 减少检查频率（增大 `interval` 参数）或清空历史记录
\`\`\`
