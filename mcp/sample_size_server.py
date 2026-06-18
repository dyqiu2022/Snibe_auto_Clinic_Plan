# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp>=1.2.0",
#     "scipy>=1.10.0",
# ]
# ///
# 上面是 PEP 723 内联依赖声明：uv run 时自动创建隔离环境并安装依赖，
# 从 GitHub 克隆后无需手动 pip install，uv run 即可启动。
"""
IVD 临床试验样本量计算 MCP Server
==================================
为临床试验方案第六章"统计学考虑"提供确定性的样本量计算与逻辑验证。

设计原则：
  - 所有公式与 NMPA《体外诊断试剂临床试验技术指导原则》及 CLSI EP09-A3 一致
  - 相关系数法、符合率法的计算结果已与现有方案模板逐例核对，完全吻合
  - 服务是无状态纯函数，便于跨项目复用

通过 stdio 暴露为 MCP 工具，由 Claude Code 自动拉起。
启动：uv run mcp/sample_size_server.py
"""
from __future__ import annotations

import math
from mcp.server.fastmcp import FastMCP
from scipy import stats

mcp = FastMCP("ivd-sample-size")


# ============================================================
# 核心计算函数
# ============================================================

def _z(alpha: float, power: float) -> tuple[float, float]:
    """返回 (Z_{1-α/2}, Z_{1-β})。"""
    return stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)


def _fisher_z(r: float) -> float:
    """Fisher's Z 转换。"""
    return 0.5 * math.log((1 + r) / (1 - r))


def calc_correlation(rho1: float, rho0: float, alpha: float, power: float,
                     dropout: float) -> dict:
    """方法(1)：基于相关系数的样本量（Dixon & Massey 公式，定量产品）。"""
    z, zb = _z(alpha, power)
    n_stat = (z + zb) ** 2 / (_fisher_z(rho1) - _fisher_z(rho0)) ** 2 + 3
    n_min = math.ceil(n_stat)
    n_enroll = math.ceil(n_stat / (1 - dropout))
    return {
        "method": "基于相关系数（Dixon & Massey）",
        "applicable": "定量产品",
        "params": {"ρ1": rho1, "ρ0": rho0, "α": alpha, "1-β": power, "脱落率": dropout},
        "formula": "n = (Z_{1-α/2} + Z_{1-β})² / [FZ(ρ1) - FZ(ρ0)]² + 3",
        "z_values": {"Z_{1-α/2}": round(z, 4), "Z_{1-β}": round(zb, 4)},
        "fisher_z": {"FZ(ρ1)": round(_fisher_z(rho1), 4), "FZ(ρ0)": round(_fisher_z(rho0), 4)},
        "n_statistical": n_min,
        "n_with_dropout": n_enroll,
    }


def calc_bland_altman(mu: float, sigma: float, delta: float,
                      alpha: float, power: float, dropout: float) -> dict:
    """方法(2)：基于 Bland-Altman 一致性分析的样本量（Lu et al. 2016，定量产品）。

    采用迭代法，使用 t 分布与卡方分布校正 SD 估计的不确定性，
    这比正态近似更接近 MedCalc 软件的结果。
    """
    z, zb = _z(alpha, power)
    threshold = z + zb  # 检验水准 + 检验效能对应的临界值
    true_loa = abs(mu) + z * sigma  # 真实一致性界限上界位置

    result = {
        "method": "基于 Bland-Altman 一致性分析（Lu et al. 2016）",
        "applicable": "定量产品",
        "params": {"μ": mu, "σ": sigma, "δ": delta, "α": alpha, "1-β": power, "脱落率": dropout},
        "true_loa_upper": round(true_loa, 4),
        "warning": None,
    }

    # 若真实 LoA 已超出可接受 δ，无论如何增加样本量都无法证明一致性
    margin = delta - true_loa
    if margin <= 0:
        result.update({
            "n_statistical": None,
            "n_with_dropout": None,
            "warning": (f"真实一致性界限上界（|μ|+1.96σ={true_loa:.2f}）已超过临床可接受偏倚 δ={delta}，"
                        "说明方法间系统差异过大，增加样本量无法证明一致性，需重新评估 μ/σ 取值。"),
        })
        return result

    # 迭代寻找最小的 n，使得 (δ - 真实LoA) / SE(LoA) ≥ 临界值
    n_found = None
    for n in range(4, 100000):
        df = n - 1
        t_val = stats.t.ppf(1 - alpha / 2, df)
        se = sigma * math.sqrt(1 / n + t_val ** 2 / (2 * df))
        if margin / se >= threshold:
            n_found = n
            break

    if n_found is None:
        result.update({"n_statistical": None, "n_with_dropout": None,
                       "warning": "在合理范围内未收敛，请检查参数。"})
        return result

    n_enroll = math.ceil(n_found / (1 - dropout))
    result.update({
        "n_statistical": n_found,
        "n_with_dropout": n_enroll,
        "note": "采用 t 分布与卡方校正的迭代法；与 MedCalc 结果可能略有差异（±10%），"
                "如需精确复现 MedCalc 数值请在 MedCalc 中复核。",
    })
    return result


def calc_agreement(p0_pos: float, pt_pos: float, p0_neg: float, pt_neg: float,
                   alpha: float, power: float, dropout: float) -> dict:
    """方法(3)：基于阳性/阴性符合率的样本量（单组目标值法，定性/定量通用）。"""
    z, zb = _z(alpha, power)

    def _n(p0, pt):
        return (z * math.sqrt(p0 * (1 - p0)) + zb * math.sqrt(pt * (1 - pt))) ** 2 / (pt - p0) ** 2

    n_pos = math.ceil(_n(p0_pos, pt_pos))
    n_neg = math.ceil(_n(p0_neg, pt_neg))
    n_total = n_pos + n_neg
    n_enroll = math.ceil(n_total / (1 - dropout))
    return {
        "method": "基于阳性/阴性符合率（单组目标值法）",
        "applicable": "定性产品（定量产品亦可使用）",
        "params": {
            "阳性 P₀": p0_pos, "阳性 P_T": pt_pos,
            "阴性 P₀": p0_neg, "阴性 P_T": pt_neg,
            "α": alpha, "1-β": power, "脱落率": dropout,
        },
        "formula": "n = [Z_{1-α/2}·√(P₀(1-P₀)) + Z_{1-β}·√(P_T(1-P_T))]² / (P_T - P₀)²",
        "z_values": {"Z_{1-α/2}": round(z, 4), "Z_{1-β}": round(zb, 4)},
        "n_positive": n_pos,
        "n_negative": n_neg,
        "n_statistical_total": n_total,
        "n_with_dropout": n_enroll,
    }


# ============================================================
# MCP 工具
# ============================================================

@mcp.tool()
def calc_correlation_sample_size(
    rho1: float, rho0: float,
    alpha: float = 0.05, power: float = 0.80, dropout: float = 0.05,
) -> dict:
    """定量产品——基于相关系数的样本量估算（Dixon & Massey 公式）。

    Args:
        rho1: 备择假设相关系数 ρ₁（考核vs对比预期相关系数，如 0.985）
        rho0: 无效假设相关系数 ρ₀（最低要求，EP09-A3 通常 ≥0.975）
        alpha: 检验水准（默认 0.05）
        power: 检验效能 1-β（默认 0.80）
        dropout: 脱落剔除率（默认 0.05）

    Returns:
        含统计最低样本量、含脱落率预计入组数、完整计算过程的字典
    """
    return calc_correlation(rho1, rho0, alpha, power, dropout)


@mcp.tool()
def calc_bland_altman_sample_size(
    mu: float, sigma: float, delta: float,
    alpha: float = 0.05, power: float = 0.80, dropout: float = 0.05,
) -> dict:
    """定量产品——基于 Bland-Altman 一致性分析的样本量估算（Lu et al. 2016）。

    Args:
        mu: 方法间预期偏倚均值 μ（%，如 0）
        sigma: 方法间预期偏倚标准差 σ（%，如 12）
        delta: 临床可接受最大偏倚 δ（%，如 30）
        alpha: 检验水准（默认 0.05）
        power: 检验效能（默认 0.80）
        dropout: 脱落剔除率（默认 0.05）

    Returns:
        含样本量的字典；若真实LoA超出δ会返回warning
    """
    return calc_bland_altman(mu, sigma, delta, alpha, power, dropout)


@mcp.tool()
def calc_agreement_sample_size(
    p0_pos: float, pt_pos: float,
    p0_neg: float, pt_neg: float,
    alpha: float = 0.05, power: float = 0.80, dropout: float = 0.05,
) -> dict:
    """定性/定量产品——基于阳性/阴性符合率的样本量估算（单组目标值法）。

    分别计算阳性组和阴性组所需最低样本量。

    Args:
        p0_pos: 阳性符合率目标值 P₀（如 0.90）
        pt_pos: 阳性符合率预期值 P_T（如 0.95）
        p0_neg: 阴性符合率目标值 P₀（如 0.90）
        pt_neg: 阴性符合率预期值 P_T（如 0.97）
        alpha: 检验水准（默认 0.05）
        power: 检验效能（默认 0.80）
        dropout: 脱落剔除率（默认 0.05）

    Returns:
        含阳性组、阴性组、总样本量、含脱落率预计入组数的字典
    """
    return calc_agreement(p0_pos, pt_pos, p0_neg, pt_neg, alpha, power, dropout)


@mcp.tool()
def validate_sample_size_logic(
    statistical_positive: int,
    statistical_negative: int,
    regulatory_positive_min: int = 0,
    regulatory_negative_min: int = 0,
    final_positive: int = 0,
    final_negative: int = 0,
    final_total: int = 0,
    dropout_rate: float = 0.05,
) -> dict:
    """验证样本量章节中各数值的逻辑链自洽性（语义级验证）。

    由 LLM 在写完第六章正文后，把正文中的确定数值作为结构化参数传入。
    做纯算术比较，不解析自然语言。

    Args:
        statistical_positive: 统计估算的阳性数（正文识别）
        statistical_negative: 统计估算的阴性数
        regulatory_positive_min: 法规最低阳性数（若法规有硬性要求）
        regulatory_negative_min: 法规最低阴性数
        final_positive: 正文"综合确定"段声明最终阳性数
        final_negative: 正文"综合确定"段声明最终阴性数
        final_total: 正文声明总样本量
        dropout_rate: 脱落率

    Returns:
        {"passed": bool, "checks": [...], "errors": [...]}
    """
    checks, errors = [], []

    req_pos = max(statistical_positive, regulatory_positive_min)
    req_neg = max(statistical_negative, regulatory_negative_min)

    if final_positive:
        ok = final_positive >= req_pos
        checks.append(f"最终阳性数 {final_positive} ≥ max(统计 {statistical_positive}, 法规 {regulatory_positive_min}) = {req_pos}: {'✓' if ok else '✗'}")
        if not ok:
            errors.append(f"最终阳性数 {final_positive} 不足，应 ≥ {req_pos}")

    if final_negative:
        ok = final_negative >= req_neg
        checks.append(f"最终阴性数 {final_negative} ≥ max(统计 {statistical_negative}, 法规 {regulatory_negative_min}) = {req_neg}: {'✓' if ok else '✗'}")
        if not ok:
            errors.append(f"最终阴性数 {final_negative} 不足，应 ≥ {req_neg}")

    if final_positive and final_negative and final_total:
        expected_min = final_positive + final_negative
        ok_total = final_total >= expected_min
        checks.append(f"总样本量 {final_total} ≥ 阳性+阴性 = {expected_min}: {'✓' if ok_total else '✗'}")
        if not ok_total:
            errors.append(f"总样本量 {final_total} < 阳性+阴性 {expected_min}")

        if dropout_rate > 0:
            needed_with_dropout = math.ceil(expected_min / (1 - dropout_rate))
            ok_drop = final_total >= needed_with_dropout
            checks.append(f"总样本量 {final_total} ≥ (阳性+阴性)/(1-脱落率) = {needed_with_dropout}: {'✓' if ok_drop else '✗'}")
            if not ok_drop:
                errors.append(f"总样本量 {final_total} 未含脱落率加成，应 ≥ {needed_with_dropout}")

    return {"passed": len(errors) == 0, "checks": checks, "errors": errors}


if __name__ == "__main__":
    mcp.run()
