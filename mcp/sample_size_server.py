#!/usr/bin/env python
"""样本量计算 MCP Server for IVD 临床试验方案。

提供 4 个工具:
- calc_correlation_sample_size (定量)
- calc_bland_altman_sample_size (定量)
- calc_agreement_sample_size (定性/定量通用)
- validate_sample_size_logic (逻辑链验证)
"""
import math
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ivd-sample-size")


def _z(p: float) -> float:
    """正态分布逆 CDF (近似)。"""
    # 简化的 Z 值表 (足够覆盖 alpha=0.05/0.01, beta=0.10/0.20)
    table = {
        0.8416: 0.20,
        0.9759: 0.10,
        1.0364: 0.15,
        1.2816: 0.10,
        1.6449: 0.05,
        1.9600: 0.025,
        2.0537: 0.02,
        2.3263: 0.01,
    }
    for z, q in table.items():
        if abs(p - z) < 0.001:
            return q
    # 兜底：双侧
    return 0.025


def fisher_z(rho: float) -> float:
    """Fisher Z 变换。"""
    return 0.5 * math.log((1 + rho) / (1 - rho))


@mcp.tool()
def calc_correlation_sample_size(
    rho0: float,
    rho1: float,
    alpha: float = 0.05,
    power: float = 0.80,
    dropout: float = 0.05,
) -> dict[str, Any]:
    """基于相关系数的样本量估算 (Dixon & Massey 法)。

    Args:
        rho0: 最低可接受相关系数 (如 0.975)
        rho1: 预期相关系数 (如 0.99)
        alpha: 检验水准
        power: 检验效能 (1-β)
        dropout: 脱落率 (如 0.05 = 5%)

    Returns:
        包含 n (最低样本量) 和 n_with_dropout (调整后入组数) 的字典。
    """
    z_alpha = 1.96 if alpha == 0.05 else 1.6449
    z_beta_table = {0.80: 0.8416, 0.85: 1.0364, 0.90: 1.2816, 0.95: 1.6449}
    z_beta = z_beta_table.get(power, 0.8416)

    fz0 = fisher_z(rho0)
    fz1 = fisher_z(rho1)
    diff = fz1 - fz0
    if diff <= 0:
        return {"error": f"rho1 ({rho1}) 必须大于 rho0 ({rho0})"}

    n = ((z_alpha + z_beta) / diff) ** 2 + 3
    n_int = math.ceil(n)
    n_with_dropout = math.ceil(n / (1 - dropout))

    return {
        "method": "Dixon-Massey correlation",
        "rho0": rho0,
        "rho1": rho1,
        "alpha": alpha,
        "power": power,
        "z_alpha_2sided": z_alpha,
        "z_beta": z_beta,
        "n_calculated": round(n, 2),
        "n_ceiled": n_int,
        "dropout_rate": dropout,
        "n_with_dropout": n_with_dropout,
    }


@mcp.tool()
def calc_bland_altman_sample_size(
    alpha: float = 0.05,
    power: float = 0.80,
    bias_mean: float = 0.0,
    bias_sd: float = 5.0,
    acceptable_bias_pct: float = 10.0,
    dropout: float = 0.05,
) -> dict[str, Any]:
    """基于 Bland-Altman 一致性分析的样本量估算 (Lu et al. 法)。

    Args:
        alpha: 检验水准
        power: 检验效能
        bias_mean: 预期偏倚均值 (%)
        bias_sd: 预期偏倚标准差 (%)
        acceptable_bias_pct: 临床可接受最大偏倚 (%)
        dropout: 脱落率

    Returns:
        样本量估算结果。
    """
    z_alpha = 1.96 if alpha == 0.05 else 1.6449
    z_beta_table = {0.80: 0.8416, 0.85: 1.0364, 0.90: 1.2816, 0.95: 1.6449}
    z_beta = z_beta_table.get(power, 0.8416)

    if bias_sd <= 0:
        return {"error": "bias_sd 必须大于 0"}

    # Lu et al. 简化公式: n = (z_α/2 + z_β)² × σ² / (δ - |μ|)²
    delta = acceptable_bias_pct - abs(bias_mean)
    if delta <= 0:
        return {"error": f"可接受偏倚 ({acceptable_bias_pct}%) 必须大于预期偏倚均值 ({abs(bias_mean)}%)"}

    n = ((z_alpha + z_beta) ** 2 * bias_sd ** 2) / (delta ** 2)
    n_int = math.ceil(n)
    n_with_dropout = math.ceil(n / (1 - dropout))

    return {
        "method": "Lu et al. Bland-Altman",
        "alpha": alpha,
        "power": power,
        "bias_mean": bias_mean,
        "bias_sd": bias_sd,
        "acceptable_bias_pct": acceptable_bias_pct,
        "delta": delta,
        "n_calculated": round(n, 2),
        "n_ceiled": n_int,
        "dropout_rate": dropout,
        "n_with_dropout": n_with_dropout,
    }


@mcp.tool()
def calc_agreement_sample_size(
    p0_pos: float,
    pt_pos: float,
    p0_neg: float,
    pt_neg: float,
    alpha: float = 0.05,
    power: float = 0.80,
    dropout: float = 0.05,
) -> dict[str, Any]:
    """基于阳性/阴性符合率的样本量估算 (单组目标值法)。

    Args:
        p0_pos: 阳性符合率目标值 P₀
        pt_pos: 阳性符合率预期值 P_T
        p0_neg: 阴性符合率目标值 P₀
        pt_neg: 阴性符合率预期值 P_T
        alpha: 检验水准
        power: 检验效能
        dropout: 脱落率

    Returns:
        阳性组、阴性组、总样本量。
    """
    z_alpha = 1.96 if alpha == 0.05 else 1.6449
    z_beta_table = {0.80: 0.8416, 0.85: 1.0364, 0.90: 1.2816, 0.95: 1.6449}
    z_beta = z_beta_table.get(power, 0.8416)

    def n_for(p0, pt):
        if pt <= p0:
            return None
        term1 = z_alpha * math.sqrt(p0 * (1 - p0))
        term2 = z_beta * math.sqrt(pt * (1 - pt))
        n = (term1 + term2) ** 2 / (pt - p0) ** 2
        return math.ceil(n)

    n_pos = n_for(p0_pos, pt_pos)
    n_neg = n_for(p0_neg, pt_neg)
    n_total = (n_pos or 0) + (n_neg or 0)
    n_with_dropout = math.ceil(n_total / (1 - dropout))

    return {
        "method": "Single-arm target value (Hypothesis test)",
        "alpha": alpha,
        "power": power,
        "p0_pos": p0_pos,
        "pt_pos": pt_pos,
        "p0_neg": p0_neg,
        "pt_neg": pt_neg,
        "n_pos_ceiled": n_pos,
        "n_neg_ceiled": n_neg,
        "n_total_ceiled": n_total,
        "dropout_rate": dropout,
        "n_with_dropout": n_with_dropout,
    }


@mcp.tool()
def validate_sample_size_logic(
    product_type: str,
    n_calculated: int,
    n_reg_min: int = 0,
    management_category: str = "第三类",
) -> dict[str, Any]:
    """验证样本量逻辑链自洽性。

    Args:
        product_type: "定性" 或 "定量"
        n_calculated: 统计计算出的样本量
        n_reg_min: 法规最低要求 (0 表示无)
        management_category: 管理类别

    Returns:
        逻辑链验证结果和最终建议样本量。
    """
    issues = []
    warnings = []

    # 范围合理性
    if product_type == "定性":
        if n_calculated < 200:
            warnings.append(f"定性产品样本量 {n_calculated} < 200，可能低于行业惯例")
        if n_calculated > 5000:
            warnings.append(f"定性产品样本量 {n_calculated} > 5000，可能过高")
    else:  # 定量
        if n_calculated < 80:
            warnings.append(f"定量产品样本量 {n_calculated} < 80，可能不足")
        if n_calculated > 2000:
            warnings.append(f"定量产品样本量 {n_calculated} > 2000，可能过高")

    # 法规交叉
    if n_reg_min > n_calculated:
        issues.append(
            f"统计估算 {n_calculated} < 法规最低 {n_reg_min} → 最终必须取 {n_reg_min}"
        )
        final_n = n_reg_min
    else:
        final_n = n_calculated

    # 机构数要求
    min_sites = 3 if management_category == "第三类" else 2
    if product_type == "定性" and n_calculated > 0:
        avg_per_site = final_n / min_sites
        if avg_per_site < 30:
            warnings.append(
                f"每机构平均入组 {avg_per_site:.0f} 例偏少，可能影响质量"
            )

    return {
        "product_type": product_type,
        "management_category": management_category,
        "min_sites_required": min_sites,
        "n_calculated": n_calculated,
        "n_reg_min": n_reg_min,
        "n_final": final_n,
        "issues": issues,
        "warnings": warnings,
        "passed": len(issues) == 0,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
