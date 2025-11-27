# AI Noter - 智能工作助手

一个基于 Web 的智能笔记系统，通过 AI 自动分类、整理和管理你的知识和任务。

## 核心特性

### 智能分类
- 自动判断内容是否应为笔记
- AI 识别笔记类型（待办事项、知识、灵感、参考等）
- 建议合并到现有笔记

### 自动整理
- AI 将复杂内容整理为结构化 Markdown
- 提取重要时间点和关键信息
- 保留原始内容用于参考

### 多种输入方式
- 剪切板自动监听（Windows 原生支持）
- 手动文本输入
- 文件拖拽上传
- URL 链接捕获

### 完整编辑功能
- 富文本编辑器
- 三视图编辑（原始、AI 整理、编辑）
- Markdown 支持
- 实时预览

### 高效管理
- 笔记分类浏览
- 快速搜索功能
- 标签系统
- 时间线视图

## 技术栈

- **前端**：Vue.js 3 + 原生 CSS（暗色主题）
- **后端**：Python Flask + REST API
- **AI**：调用阿里云通义千问 API
- **存储**：本地 Markdown 文件 + JSON 索引

## 项目结构

```
ai-noter/
├── 前端（Web UI）
│   └── index.html                # Vue.js 应用
├── 后端（API 服务）
│   ├── app.py                    # Flask 主应用
│   ├── config.py                 # 配置管理
│   ├── requirements.txt           # Python 依赖
├── 系统集成
│   ├── main.py                   # 一键启动脚本
│   ├── clipboard_monitor.py      # 剪切板监听
├── 启动脚本
│   ├── run_system.bat            # Windows
│   ├── run_system.sh             # Linux/Mac
├── 数据存储
│   └── data/
│       ├── notes/                # Markdown 笔记
│       └── index.json            # 索引文件
└── 文档
    ├── README.md                 # 本文件
    ├── QUICK_START.md            # 快速开始
    ├── DEPLOY.md                 # 部署指南
    ├── README_BACKEND.md         # 后端文档
    ├── README_CLIPBOARD.md       # 剪切板文档
    └── README_FRONTEND.md        # 前端文档
```

## 快速开始

### 最快开始方式

```bash
# Windows
run_system.bat

# macOS/Linux
bash run_system.sh
```

详见 [QUICK_START.md](./QUICK_START.md)

## API 文档

### 分类 API

**POST /api/classify-content**

判断内容是否为笔记及其类型。

请求：
```json
{
  "content": "用户复制的内容"
}
```

响应：
```json
{
  "is_note": true,
  "note_type": "待办事项",
  "confidence": 0.95,
  "reason": "包含明确的任务和截止日期"
}
```

### 整理 API

**POST /api/organize-content**

将内容整理为结构化 Markdown。

请求：
```json
{
  "content": "待整理的内容",
  "note_type": "零散知识"
}
```

响应：
```json
{
  "organized_markdown": "# 标题\n\n内容...",
  "key_dates": [
    {"date": "2024-01-15", "description": "事件"}
  ],
  "key_points": ["要点1", "要点2"],
  "summary": "一句话总结"
}
```

### 笔记管理 API

参见 [README_BACKEND.md](./README_BACKEND.md) 详细 API 文档。

## 配置

### 环境变量

创建 `.env` 文件：

```env
# 必需：通义千问 API Key
DASHSCOPE_API_KEY=sk-xxxxx

# 可选
FLASK_ENV=development
FLASK_DEBUG=False
CLIPBOARD_CHECK_INTERVAL=1
LOG_LEVEL=INFO
```

## 数据存储

### 笔记文件格式

每个笔记保存为 Markdown 文件，包含：
- 原始内容（用户复制或输入的内容）
- AI 整理内容（AI 组织整理的结构化内容）
- 用户编辑内容（用户后续编辑的内容）
- 元数据（创建时间、类型、标签等）

### 索引文件

`data/index.json` 维护所有笔记的快速索引：

```json
[
  {
    "id": "20240115_120000",
    "title": "笔记标题",
    "type": "零散知识",
    "summary": "一句话总结",
    "file_name": "20240115_120000_零散知识.md",
    "created_at": "2024-01-15T12:00:00",
    "updated_at": "2024-01-15T12:00:00",
    "tags": ["标签1", "标签2"]
  }
]
```

## 故障排查

### 后端错误

详见 [README_BACKEND.md](./README_BACKEND.md)

### 剪切板问题

详见 [README_CLIPBOARD.md](./README_CLIPBOARD.md)

### 前端问题

详见 [README_FRONTEND.md](./README_FRONTEND.md)

### 部署问题

详见 [DEPLOY.md](./DEPLOY.md)

## 性能指标

- 后端 API 响应时间：< 2 秒
- 剪切板检查间隔：1 秒（可配置）
- 前端加载时间：< 1 秒
- 支持笔记数量：无限制（受磁盘空间限制）

## 安全性

- 所有数据存储在本地，不上传到服务器
- API Key 存储在本地 `.env` 文件
- 支持 HTTPS（可通过 Nginx 反向代理配置）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- GitHub: [项目链接]
- 邮件: [email]

## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 支持笔记创建、编辑、删除
- AI 分类和整理功能
- 剪切板自动监听
- Web UI 完整功能

**3.1.0**
- ✅ 完成多端同步功能 - 支持移动端和桌面端实时同步
- ✅ 优化搜索功能 - 支持关键词高亮和全文搜索
- ✅ 新增笔记分享功能 - 支持生成分享链接
- ✅ 优化 UI 界面 - 提升用户体验
- ✅ 修复已知 bug 和性能优化

**待实现功能**

### 内容输入与捕获

- ✅ 支持多种输入方式（剪切板监听、手动输入、文件上传）
- ✅ 实现智能内容捕获（可识别网页、PDF、图片、表格等）
- ✅ 建立系统托盘入口与快捷键
- [ ] 网页内容提取与整理：从网页中提取主要内容，并自动整理为结构化笔记
- [ ] 剪切板监听与智能处理：持续监控系统剪切板，自动处理复制的内容并将其添加到笔记中

### 智能提醒系统

- ✅ 实现基于内容的智能提醒（时间、地点、上下文等）
- ✅ 支持用户自定义提醒规则

### 笔记管理功能

- [ ] AI 自动分类与标签提取：利用 AI 将内容自动分类为不同笔记类型（如待办事项、零散知识、灵感想法等），并提取关键信息作为标签
- [ ] 内容自动总结：对笔记内容进行自动总结，生成简洁的内容摘要，提升浏览和回顾笔记的效率
- ✅ 支持关联笔记与知识图谱构建
- ✅ 实现笔记内容快速检索

### 系统优化

- ✅ 实现本地与云端双存储机制
- ✅ 确保用户数据隐私安全

**祝你使用愉快！如有问题，欢迎反馈。**