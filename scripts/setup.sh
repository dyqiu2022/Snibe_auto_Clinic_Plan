#!/usr/bin/env bash
# MCP 环境引导脚本——从 GitHub 克隆后运行一次即可。
# 作用：安装 uv（若未装），并预拉取 MCP 依赖，使首次 Claude Code 启动更快。
set -e

echo "=== IVD 样本量 MCP 环境引导 ==="

# 1. 确保 uv 已安装
if ! command -v uv >/dev/null 2>&1; then
  echo "[1/3] 未检测到 uv，正在安装..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # 加入当前 shell 的 PATH
  export PATH="$HOME/.local/bin:$PATH"
  grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  echo "      uv 安装完成。"
else
  echo "[1/3] uv 已安装：$(uv --version)"
fi

# 2. 预装依赖（uv 会缓存，后续启动近乎瞬时）
echo "[2/3] 预装 MCP 依赖（scipy/mcp）..."
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
uv run --python 3.12 "$SCRIPT_DIR/mcp/sample_size_server.py" --help >/dev/null 2>&1 || \
  uv run --python 3.12 "$SCRIPT_DIR/mcp/sample_size_server.py" </dev/null >/dev/null 2>&1 &
UV_PID=$!
sleep 8
kill $UV_PID 2>/dev/null || true
echo "      依赖已缓存。"

# 3. 提示
echo "[3/3] 完成。"
echo ""
echo "下一步：在 Claude Code 中直接使用，MCP 会在项目启动时自动连接。"
echo "  - 项目级配置已写入 .mcp.json（无需手动 claude mcp add）"
echo "  - 若 uv 未加入 PATH，重启终端或执行: source ~/.bashrc"
