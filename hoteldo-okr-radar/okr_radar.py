"""okr_radar.py — Motor de análisis para hoteldo-okr-radar.

Uso:
    python3 okr_radar.py input.json

Toma un JSON con datos de OKRs y devuelve:
  1. Narrativa ejecutiva en español (stdout)
  2. JSON estructurado (archivo .radar.json junto al input)
"""

import json
import sys
from datetime import datetime, date
from pathlib import Path

# ── Constantes ──────────────────────────────────────────────────────────

SQUADS = [
    "API",
    "B2B Commercial & Engagement",
    "B2B Efficiency & Support",
    "Rewards B2B2C",
]

STATUS_COLORS = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
STATUS_LABELS = {"green": "En camino", "yellow": "Atrasado", "red": "En riesgo crítico"}

# ── Helpers ─────────────────────────────────────────────────────────────

def _clamp(v, lo=0.0):
    return max(lo, v)


def _fmt_money(v):
    if abs(v) >= 1_000_000:
        return f"${v / 1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:,.0f}"


def _week_label(week_str):
    """Convierte 2026-02-10 → 'Semana del 10-Feb'."""
    try:
        d = datetime.strptime(week_str, "%Y-%m-%d")
        months_es = [
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
        ]
        return f"Semana del {d.day}-{months_es[d.month - 1]}"
    except (ValueError, TypeError):
        return week_str


def _linear_regression(weeks, values):
    """Regresión lineal simple (y = a*x + b). Devuelve (slope, intercept)."""
    n = len(weeks)
    if n < 2:
        return (0.0, values[0] if values else 0.0)
    sum_x = sum(weeks)
    sum_y = sum(values)
    sum_xy = sum(w * v for w, v in zip(weeks, values))
    sum_xx = sum(w * w for w in weeks)
    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        return (0.0, values[0])
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return (slope, intercept)


# ── Análisis de un KR ───────────────────────────────────────────────────

def analyze_kr(kr, weeks_elapsed, weeks_total):
    """Analiza un KR individual y devuelve el dict de resultados."""
    current = kr["current_value"]
    target = kr["target_value"]
    baseline = kr["baseline_value"]

    # Progreso
    delta_total = target - baseline
    if delta_total == 0:
        progress_pct = 100.0 if current >= target else 0.0
    else:
        progress_pct = _clamp((current - baseline) / delta_total * 100)

    # Progreso esperado
    expected_pct = (weeks_elapsed / weeks_total * 100) if weeks_total > 0 else 0.0

    # Velocidad
    velocity = (progress_pct / expected_pct) if expected_pct > 0 else 0.0

    # Semáforo
    if progress_pct >= expected_pct * 0.95:
        status = "green"
    elif progress_pct >= expected_pct * 0.75:
        status = "yellow"
    else:
        status = "red"

    # Proyección con regresión lineal
    history = kr.get("weekly_history", [])
    projected_week = None
    weekly_trend = "unknown"
    if len(history) >= 2:
        weeks_idx = list(range(len(history)))
        vals = [h["value"] for h in history]
        slope, intercept = _linear_regression(weeks_idx, vals)
        if slope > 0 and target > current:
            weeks_to_target = (target - intercept) / slope
            projected_week = int(round(weeks_to_target))
            weekly_trend = "stable_growth" if slope > 0 else "declining"
        elif slope <= 0:
            weekly_trend = "stagnant" if slope == 0 else "declining"
            projected_week = None
        else:
            weekly_trend = "accelerating"
            projected_week = None  # ya superó el target o muy cerca

    # Detección de anomalías
    anomalies = []
    if len(history) >= 2:
        vals = [h["value"] for h in history]
        for i in range(1, len(vals)):
            if vals[i - 1] > 0:
                change = (vals[i] - vals[i - 1]) / vals[i - 1]
                if abs(change) > 0.20:
                    anomalies.append({
                        "type": "sharp_change",
                        "week": history[i].get("week", f"semana {i+1}")
                            if isinstance(history[i], dict) else f"semana {i+1}",
                        "change_pct": round(change * 100, 1),
                    })
        # Estancamiento
        if len(vals) >= 4:
            last_3 = vals[-3:]
            if all(v == last_3[0] for v in last_3):
                anomalies.append({
                    "type": "stagnation",
                    "detail": "Sin crecimiento en las últimas 3 semanas",
                })
        # Declive
        if vals[-1] < vals[-2]:
            anomalies.append({
                "type": "decline",
                "detail": f"Valor actual ({_fmt_money(vals[-1])}) menor a semana anterior ({_fmt_money(vals[-2])})",
            })

    # Recomendación
    if status == "red":
        recommendation = f"Riesgo crítico: progreso {progress_pct:.0f}% vs {expected_pct:.0f}% esperado. Requiere intervención inmediata."
    elif status == "yellow":
        recommendation = f"Atrasado: progreso {progress_pct:.0f}% vs {expected_pct:.0f}% esperado. Revisar blockers y ajustar plan."
    else:
        recommendation = f"En camino: progreso {progress_pct:.0f}% vs {expected_pct:.0f}% esperado. Mantener el ritmo."

    return {
        "id": kr.get("id", "?"),
        "description": kr.get("description", ""),
        "current_value": current,
        "target_value": target,
        "baseline_value": baseline,
        "progress_pct": round(progress_pct, 1),
        "expected_progress_pct": round(expected_pct, 1),
        "velocity": round(velocity, 2),
        "status": status,
        "status_label": STATUS_LABELS[status],
        "projected_completion_week": projected_week,
        "on_track": status == "green",
        "anomalies": anomalies,
        "weekly_trend": weekly_trend,
        "recommendation": recommendation,
    }


# ── Narrativa ───────────────────────────────────────────────────────────

def build_narrative(data, results):
    """Genera el texto ejecutivo en español."""
    lines = []
    squad = data.get("squad", "—")
    quarter = data.get("quarter", "—")
    objective = data.get("objective", "—")
    lines.append(f"📊 RADAR DE OKRs — {quarter} — Squad {squad}")
    lines.append("")
    lines.append(f"Objetivo: {objective}")
    lines.append("")

    summary = results["summary"]
    lines.append(
        f"Resumen: {summary['green']} 🟢  {summary['yellow']} 🟡  {summary['red']} 🔴  "
        f"→ Salud general: {STATUS_COLORS.get(summary['overall_health'], '⚪')}"
    )
    lines.append("")

    for kr in results["krs"]:
        icon = STATUS_COLORS[kr["status"]]
        lines.append(f"{icon} KR {kr['id']} — {kr['description']}")
        lines.append(
            f"  {kr['status_label']} ({kr['progress_pct']:.0f}% de progreso vs "
            f"{kr['expected_progress_pct']:.0f}% esperado)"
        )
        lines.append(
            f"  Actual: {_fmt_money(kr['current_value'])} / "
            f"Target: {_fmt_money(kr['target_value'])}"
        )
        lines.append(f"  Velocidad: {kr['velocity']:.2f}x")
        if kr["projected_completion_week"] is not None:
            on_time = kr["projected_completion_week"] <= _weeks_total_from_data(data)
            suffix = " (a tiempo)" if on_time else f" (semana {kr['projected_completion_week']})"
            lines.append(f"  Proyección: cumplimiento en {suffix}")
        else:
            if kr["weekly_trend"] in ("stagnant", "declining"):
                lines.append("  Proyección: sin cumplimiento proyectado con tendencia actual")
            else:
                lines.append("  Proyección: en camino o superado")
        if kr["anomalies"]:
            for a in kr["anomalies"]:
                detail = a.get("detail", f"{a.get('type', '?')} en {a.get('week', '?')}")
                lines.append(f"  ⚠️ {detail}")
        lines.append(f"  💡 {kr['recommendation']}")
        lines.append("")

    return "\n".join(lines)


def _weeks_total_from_data(data):
    """Intenta inferir semanas totales del trimestre (default 26 para H1)."""
    q = data.get("quarter", "")
    if "H1" in q or "h1" in q:
        return 26
    if "H2" in q or "h2" in q:
        return 26
    return 13  # default trimestral


# ── Pipeline principal ──────────────────────────────────────────────────

def run_radar(data):
    """Ejecuta el análisis completo. Devuelve (narrativa, json_result)."""
    weeks_total = _weeks_total_from_data(data)
    history = data.get("krs", [{}])[0].get("weekly_history", []) if data.get("krs") else []
    weeks_elapsed = len(history) if history else weeks_total // 2  # fallback mitad del trimestre

    kr_results = []
    green = yellow = red = 0
    for kr in data.get("krs", []):
        r = analyze_kr(kr, weeks_elapsed, weeks_total)
        kr_results.append(r)
        if r["status"] == "green":
            green += 1
        elif r["status"] == "yellow":
            yellow += 1
        else:
            red += 1

    overall = "green" if red == 0 and yellow == 0 else ("red" if red > yellow else "yellow")

    results = {
        "objective": data.get("objective", ""),
        "squad": data.get("squad", ""),
        "quarter": data.get("quarter", ""),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total_krs": len(kr_results),
            "green": green,
            "yellow": yellow,
            "red": red,
            "overall_health": overall,
        },
        "krs": kr_results,
    }

    narrative = build_narrative(data, results)
    return narrative, results


# ── CLI ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 okr_radar.py input.json")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    narrative, results = run_radar(data)

    # Narrativa a stdout
    print(narrative)

    # JSON a archivo
    out_path = input_path.with_suffix(".radar.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📁 JSON estructurado: {out_path}")


if __name__ == "__main__":
    main()
