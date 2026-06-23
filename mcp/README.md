# MCP 样本量计算服务器

## 工具列表

| 工具 | 用途 | 适用 |
|------|------|------|
| `calc_correlation_sample_size` | Dixon-Massey 相关系数法 | 定量 |
| `calc_bland_altman_sample_size` | Lu et al. Bland-Altman 法 | 定量 |
| `calc_agreement_sample_size` | 单组目标值法（符合率） | 定性/定量 |
| `validate_sample_size_logic` | 逻辑链验证 | 通用 |

## 配置

参见 `config.json`，本项目级配置由 WorkBuddy 的 mcp.json 引用：

```json
{
  "command": "uv",
  "args": ["run", "--python", "3.12", "D:\\work buddy\\clinic_codingAgentTest\\mcp\\sample_size_server.py"]
}
```

## 依赖

通过 uv 自动管理（PEP 723 内联依赖声明）：
- mcp[cli]>=1.0
- python>=3.12
