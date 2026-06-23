# IVD 样本量计算 MCP Server

为临床试验方案第六章"统计学考虑"提供确定性的样本量计算与逻辑验证。

## 可移植性机制（克隆即用）

本 MCP Server 采用 **uv + PEP 723 内联依赖** 方案，确保从 GitHub 克隆后无需任何手动配置即可运行。

### 工作原理

```
.mcp.json (项目级，已提交)
  └─ command: uv run ${CLAUDE_PROJECT_DIR}/mcp/sample_size_server.py
          │
          ▼
sample_size_server.py 顶部 PEP 723 块声明依赖
  # /// script
  # dependencies = ["mcp>=1.2.0", "scipy>=1.10.0"]
  # ///
          │
          ▼
uv run 自动：创建隔离环境 → 安装依赖（全局缓存）→ 启动 server
```

- **零系统依赖**：只依赖 `uv`（一个单文件二进制），不污染系统 Python
- **路径无关**：用 `${CLAUDE_PROJECT_DIR}` 变量，换机器/换用户名都不影响
- **全局缓存**：scipy 等依赖装一次后全局缓存，后续启动近乎瞬时
- **版本锁定**：依赖版本写在脚本顶部，所有人一致

### 在新机器上启用（3 步）

```bash
# 1. 克隆项目
git clone git@github.com:dyqiu2022/Snibe_auto_Clinic_Plan.git
cd Snibe_auto_Clinic_Plan

# 2. 运行引导脚本（装 uv + 预拉依赖）
bash scripts/setup.sh

# 3. 启动 Claude Code，MCP 自动连接
claude
```

> 若系统已有 uv（`curl -LsSf https://astral.sh/uv/install.sh | sh`），第 2 步可跳过——Claude Code 首次启动时会自动拉起 server 并按需装依赖。

## 提供的工具

| 工具名 | 用途 | 适用 |
|--------|------|------|
| `calc_correlation_sample_size` | 相关系数法样本量（Dixon & Massey） | 定量 |
| `calc_bland_altman_sample_size` | Bland-Altman 法样本量（Lu et al. 2016） | 定量 |
| `calc_agreement_sample_size` | 阳性/阴性符合率法样本量（单组目标值法） | 定性/定量 |
| `validate_sample_size_logic` | 样本量逻辑链自洽性验证（语义级） | 通用 |

### 计算正确性

所有公式已与现有临床试验方案模板逐例核对：

| 方法 | 输入参数 | 模板值 | MCP 输出 |
|------|---------|--------|---------|
| 相关系数法 | ρ₁=0.985, ρ₀=0.975, α=0.05, β=0.20 | n=121 | ✓ 121 |
| 符合率法-阳性 | P₀=0.90, P_T=0.95 | n=239 | ✓ 239 |
| 符合率法-阴性 | P₀=0.90, P_T=0.97 | n=110 | ✓ 110 |

> Bland-Altman 法采用 t 分布 + 卡方校正的迭代算法，与 MedCalc 结果可能存在 ±10% 差异。如需精确复现 MedCalc 数值，建议在 MedCalc 软件中复核。

## 手动测试

```bash
# 直接运行（uv 自动建环境）
uv run --python 3.12 mcp/sample_size_server.py

# 发送测试请求
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"calc_agreement_sample_size","arguments":{"p0_pos":0.90,"pt_pos":0.95,"p0_neg":0.90,"pt_neg":0.97}}}' \
| uv run --python 3.12 mcp/sample_size_server.py
```

## 无 uv 的备选方案

若环境无法安装 uv，可用传统 venv：

```bash
python3 -m venv .venv
.venv/bin/pip install mcp scipy
.venv/bin/python mcp/sample_size_server.py
```

并将 `.mcp.json` 的 command 改为 `.venv/bin/python`、args 改为 `${CLAUDE_PROJECT_DIR}/mcp/sample_size_server.py`。
