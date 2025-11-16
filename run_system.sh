#!/bin/bash
# Linux/Mac 启动脚本

echo "🚀 启动 AI Noter 系统..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3 环境"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 启动系统
echo "▶️  启动系统..."
python main.py
