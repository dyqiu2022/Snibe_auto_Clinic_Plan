# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "scipy>=1.10.0",
# ]
# ///
"""
IVD 临床试验样本量计算 CLI
==========================
确定性样本量计算工具。不依赖 MCP 协议，可直接通过命令行调用。

用法:
  uv run scripts/sample_size_calc.py agreement 0.90 0.97 0.90 0.97 0.05 0.80 0.05
  uv run scripts/sample_size_calc.py correlation 0.985 0.975 0.05 0.80 0.05
  uv run scripts/sample_size_calc.py bland-altman 0 12 30 0.05 0.80 0.05
  uv run scripts/sample_size_calc.py validate <json_args>

输出: JSON (stdout)
"""
import json, math, sys
from scipy import stats


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
    return {
        "method": "基于相关系数（Dixon & Massey）",
        "applicable": "定量产品",
        "params": {"ρ1": rho1, "ρ0": rho0, "α": alpha, "1-β": power, "脱落率": dropout},
        "formula": "n = (Z_{1-α/2} + Z_{1-β})² / [FZ(ρ1) - FZ(ρ0)]² + 3",
        "z_values": {"Z_{1-α/2}": round(z, 4), "Z_{1-β}": round(zb, 4)},
        "fisher_z": {"FZ(ρ1)": round(_fisher_z(rho1), 4),
                      "FZ(ρ0)": round(_fisher_z(rho0), 4)},
        "n_statistical": math.ceil(n_stat),
        "n_with_dropout": math.ceil(n_stat / (1 - dropout)),
    }


def calc_bland_altman(mu: float, sigma: float, delta: float,
                      alpha: float, power: float, dropout: float) -> dict:
    """方法(2)：基于 Bland-Altman 一致性分析的样本量（Lu et al. 2016，定量产品）。"""
    z, zb = _z(alpha, power)
    threshold = z + zb
    true_loa = abs(mu) + z * sigma

    result = {
        "method": "基于 Bland-Altman 一致性分析（Lu et al. 2016）",
        "applicable": "定量产品",
        "params": {"μ": mu, "σ": sigma, "δ": delta, "α": alpha, "1-β": power, "脱落率": dropout},
        "true_loa_upper": round(true_loa, 4),
    }

    margin = delta - true_loa
    if margin <= 0:
        result["warning"] = (
            f"真实一致性界限上界（|μ|+1.96σ={true_loa:.2f}）已超过临床可接受偏倚 δ={delta}，"
            "说明方法间系统差异过大，增加样本量无法证明一致性，需重新评估 μ/σ 取值。"
        )
        return result

    n_found = None
    for n in range(4, 100000):
        df = n - 1
        t_val = stats.t.ppf(1 - alpha / 2, df)
        se = sigma * math.sqrt(1 / n + t_val ** 2 / (2 * df))
        if margin / se >= threshold:
            n_found = n
            break

    if n_found is None:
        result["warning"] = "在合理范围内未收敛，请检查参数。"
        return result

    result.update({
        "n_statistical": n_found,
        "n_with_dropout": math.ceil(n_found / (1 - dropout)),
        "note": "采用 t 分布与卡方校正的迭代法；与 MedCalc 结果可能略有差异（±10%）。",
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
    return {
        "method": "基于阳性/阴性符合率（单组目标值法）",
        "applicable": "定性产品（定量产品亦可使用）",
        "params": {"阳性P₀": p0_pos, "阳性P_T": pt_pos,
                    "阴性P₀": p0_neg, "阴性P_T": pt_neg,
                    "α": alpha, "1-β": power, "脱落率": dropout},
        "formula": "n = [Z_{1-α/2}·√(P₀(1-P₀)) + Z_{1-β}·√(P_T(1-P_T))]² / (P_T - P₀)²",
        "z_values": {"Z_{1-α/2}": round(z, 4), "Z_{1-β}": round(zb, 4)},
        "n_positive": n_pos,
        "n_negative": n_neg,
        "n_statistical_total": n_pos + n_neg,
        "n_with_dropout": math.ceil((n_pos + n_neg) / (1 - dropout)),
    }


def validate(statistical_positive: int, statistical_negative: int,
             regulatory_positive_min: int = 0, regulatory_negative_min: int = 0,
             final_positive: int = 0, final_negative: int = 0,
             final_total: int = 0, dropout_rate: float = 0.05) -> dict:
    """验证样本量逻辑链自洽性。"""
    checks, errors = [], []

    req_pos = max(statistical_positive, regulatory_positive_min)
    req_neg = max(statistical_negative, regulatory_negative_min)

    for label, final, req in [("阳性", final_positive, req_pos),
                               ("阴性", final_negative, req_neg)]:
        if final:
            ok = final >= req
            checks.append(
                f"最终{label}数 {final} ≥ max(统计, 法规) = {req}: {'✓' if ok else '✗'}")
            if not ok:
                errors.append(f"最终{label}数 {final} 不足，应 ≥ {req}")

    if final_positive and final_negative and final_total:
        expected_min = final_positive + final_negative
        ok = final_total >= expected_min
        checks.append(
            f"总样本量 {final_total} ≥ {label}+... = {expected_min}: {'✓' if ok else '✗'}")
        if not ok:
            errors.append(f"总样本量 {final_total} < {expected_min}")

        if dropout_rate > 0:
            needed = math.ceil(expected_min / (1 - dropout_rate))
            ok_d = final_total >= needed
            checks.append(
                f"总样本量 {final_total} ≥ 含脱落率 = {needed}: {'✓' if ok_d else '✗'}")
            if not ok_d:
                errors.append(f"总样本量 {final_total} 未含脱落率加成，应 ≥ {needed}")

    return {"passed": len(errors) == 0, "checks": checks, "errors": errors}


# ---- CLI ----
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/sample_size_calc.py <method> [args...]", file=sys.stderr)
        print("  agreement <p0_pos> <pt_pos> <p0_neg> <pt_neg> <alpha> <power> <dropout>", file=sys.stderr)
        print("  correlation <rho1> <rho0> <alpha> <power> <dropout>", file=sys.stderr)
        print("  bland-altman <mu> <sigma> <delta> <alpha> <power> <dropout>", file=sys.stderr)
        sys.exit(1)

    method = sys.argv[1]
    args = [float(x) for x in sys.argv[2:]]

    if method == "agreement":
        result = calc_agreement(*args)
    elif method == "correlation":
        result = calc_correlation(*args)
    elif method == "bland-altman":
        result = calc_bland_altman(*args)
    elif method == "validate":
        result = validate(*args)
    else:
        print(f"Unknown method: {method}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))
