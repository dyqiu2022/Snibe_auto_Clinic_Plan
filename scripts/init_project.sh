#!/usr/bin/env bash
# 初始化新项目骨架：创建标准目录结构 + 拷贝项目信息模板。
# 用法：bash scripts/init_project.sh <项目名>
set -e

if [ -z "$1" ]; then
  echo "用法: bash scripts/init_project.sh <项目名>"
  echo "示例: bash scripts/init_project.sh 心肌肌钙蛋白化学发光"
  exit 1
fi

PROJECT_NAME="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_DIR="$ROOT/projects/$PROJECT_NAME"

if [ -d "$PROJECT_DIR" ]; then
  echo "错误：项目目录已存在 → $PROJECT_DIR"
  exit 1
fi

# 创建标准目录结构
mkdir -p "$PROJECT_DIR"/{说明书/考核试剂,说明书/对比试剂,指导原则,专家共识,竞品信息,审评报告}

# 拷贝项目信息模板
if [ -f "$ROOT/templates/项目信息.md.template" ]; then
  cp "$ROOT/templates/项目信息.md.template" "$PROJECT_DIR/项目信息.md"
fi

echo "=== 项目骨架已创建 ==="
echo "路径: $PROJECT_DIR"
echo ""
echo "目录结构："
find "$PROJECT_DIR" -type d | sed "s|$PROJECT_DIR|.|" | sort
echo ""
echo "下一步："
echo "  1. 把考核试剂 IFU(.md) 放入 说明书/考核试剂/"
echo "  2. 把对比试剂 IFU(.md) 放入 说明书/对比试剂/"
echo "  3. 把相关指导原则(.md) 放入 指导原则/"
echo "  4. (可选) 专家共识/竞品信息/审评报告 各放入对应目录"
echo "  5. 运行: /ivd-00-orchestrator 项目名=$PROJECT_NAME"
