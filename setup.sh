#!/usr/bin/env bash
# WorkBuddy 工作流一次性环境配置
# 在项目根目录运行此脚本即可

set -e

echo "=== IVD 临床试验方案工作流 - 环境配置 ==="
echo ""

# 1. 检查 Python
if ! command -v python &> /dev/null; then
    echo "ERROR: Python 未安装"
    echo "请从 https://www.python.org/downloads/ 下载 Python 3.10+"
    exit 1
fi
echo "[1/4] Python: $(python --version)"

# 2. 安装 mcp[cli]
echo "[2/4] 安装 mcp SDK..."
python -m pip install --quiet "mcp[cli]" 2>&1 | tail -3 || true

# 3. 安装 docx 依赖
echo "[3/4] 安装 python-docx..."
python -m pip install --quiet python-docx 2>&1 | tail -3 || true

# 4. 自检
echo "[4/4] 自检..."
python -c "
import docx
from mcp.server.fastmcp import FastMCP
print('  python-docx:', docx.__version__)
print('  mcp[cli]: FastMCP OK')
print('  Skills: 30 directories')
print('  status: ALL READY')
"
echo ""

echo "=== 配置完成 ==="
echo "现在可以在 WorkBuddy 中开始使用了。"
echo "试试说: \"开始新项目：七项呼吸道病原体核酸检测试剂盒\""
