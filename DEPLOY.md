# 部署指南

## 系统要求

- Python 3.8+
- 现代浏览器（Chrome/Firefox/Safari/Edge）
- Windows/macOS/Linux

## 快速开始

### 1. 克隆或下载项目

\`\`\`bash
git clone <repository-url>
cd ai-noter
\`\`\`

### 2. 安装依赖

#### Windows

\`\`\`batch
# 创建虚拟环境
python -m venv venv
venv\\Scripts\\activate

# 安装依赖
pip install -r requirements.txt

# Windows 专用：post-install pywin32
python Scripts/pywin32_postinstall.py -install
\`\`\`

#### Linux/macOS

\`\`\`bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
\`\`\`

### 3. 配置环境变量

创建 \`.env\` 文件：

\`\`\`env
DASHSCOPE_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=False
\`\`\`

### 4. 启动系统

#### 一键启动（推荐）

\`\`\`bash
# Windows
run_system.bat

# Linux/macOS
bash run_system.sh
\`\`\`

#### 或手动启动

**终端 1：启动后端**
\`\`\`bash
python app.py
\`\`\`

**终端 2：启动剪切板监听**
\`\`\`bash
python clipboard_monitor.py
\`\`\`

**浏览器：打开前端**
\`\`\`
在浏览器中打开 index.html
\`\`\`

## 文件结构

\`\`\`
ai-noter/
├── app.py                      # Flask 后端主文件
├── clipboard_monitor.py        # 剪切板监听器
├── main.py                     # 系统启动器
├── config.py                   # 配置管理
├── index.html                  # 前端 Vue 应用
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量（本地）
├── run_system.bat              # Windows 启动脚本
├── run_system.sh               # Linux/Mac 启动脚本
│
├── data/                       # 数据目录
│   ├── notes/                  # Markdown 笔记文件
│   └── index.json              # 笔记索引
│
├── clipboard_history.json      # 剪切板历史
└── README.md                   # 项目文档
\`\`\`

## 故障排查

### 后端无法启动

**问题**：\`Address already in use\`
**解决**：
\`\`\`bash
# 杀死占用端口的进程
# Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5001
kill -9 <PID>
\`\`\`

### 剪切板监听不工作（Windows）

**问题**：\`ModuleNotFoundError: No module named 'win32clipboard'\`
**解决**：
\`\`\`bash
python Scripts/pywin32_postinstall.py -install
\`\`\`

### 前端无法连接后端

**问题**：CORS 错误或连接拒绝
**解决**：
- 确保后端运行在 \`http://127.0.0.1:5001\`
- 检查防火墙设置
- 在 \`index.html\` 中验证 API_BASE 地址

### 通义千问 API 返回错误

**问题**：\`API Error\` 或 \`Invalid API Key\`
**解决**：
- 在 \`.env\` 中检查 API Key 是否正确
- 确保 API Key 有效且未过期
- 检查网络连接

## 本地开发

### 启用调试模式

编辑 \`.env\`：
\`\`\`env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
\`\`\`

### 查看后端日志

后端会输出详细日志到控制台。

### 浏览器开发者工具

按 F12 打开浏览器开发者工具，在 Console 标签查看 JavaScript 错误。

## 性能优化建议

1. **减少剪切板检查频率**
   - 在 \`.env\` 中设置 \`CLIPBOARD_CHECK_INTERVAL=2\` 或更高

2. **限制索引大小**
   - 定期清理旧笔记，设置 \`CLIPBOARD_HISTORY_LIMIT\`

3. **启用缓存**
   - 前端已启用浏览器缓存，重复加载笔记会更快

## 升级和维护

### 更新依赖

\`\`\`bash
pip install --upgrade -r requirements.txt
\`\`\`

### 备份数据

\`\`\`bash
# 备份所有笔记和索引
cp -r data/ data_backup_$(date +%Y%m%d)
cp clipboard_history.json clipboard_history_backup_$(date +%Y%m%d).json
\`\`\`

## 生产部署

### 使用 Gunicorn（Linux/Mac）

\`\`\`bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
\`\`\`

### 使用 Waitress（Windows）

\`\`\`bash
pip install waitress
waitress-serve --port=5001 app:app
\`\`\`

### 使用 Nginx 反向代理

配置 Nginx 转发请求到 Flask，并添加 SSL/TLS 支持。

## 许可证

MIT License
\`\`\`
\`\`\`
