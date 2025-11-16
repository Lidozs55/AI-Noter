# 智能工作助手 - 后端服务

## 快速开始

### 1. 安装依赖

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. 配置环境变量

创建 `.env` 文件，配置通义千问 API Key：

\`\`\`
DASHSCOPE_API_KEY=your_api_key_here
\`\`\`

### 3. 运行服务

\`\`\`bash
python app.py
\`\`\`

服务将在 `http://127.0.0.1:5001` 启动

## API 端点

### 分类与整理

- **POST /api/classify-content** - 分类内容是否为笔记及其类型
- **POST /api/suggest-merge** - 建议是否合并到现有笔记
- **POST /api/organize-content** - 整理内容为 Markdown 并提取时间点

### 笔记管理

- **POST /api/save-note** - 保存笔记
- **GET /api/notes** - 获取所有笔记
- **GET /api/notes/<id>** - 获取单个笔记
- **PUT /api/notes/<id>/edit** - 编辑笔记
- **DELETE /api/notes/<id>** - 删除笔记
- **GET /api/search** - 搜索笔记

## 数据存储结构

\`\`\`
data/
├── notes/
│   ├── 20240115_120000_待办事项.md
│   ├── 20240115_120030_零散知识.md
│   └── ...
└── index.json
\`\`\`

## 文件格式

每个笔记文件包含：
- 原始内容
- AI 整理的 Markdown
- 用户编辑的内容
- 元数据（创建时间、类型、摘要等）
\`\`\`
