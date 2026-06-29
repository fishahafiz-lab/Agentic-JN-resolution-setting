"""Agent C — Executive Brief & Enforcement Recommendations"""
from typing import Any


class AgentCResult(dict):
    def __init__(self, alert_status_label: str, alert_color_code: str,
                 school_name: str, state: str, enforcement_actions: list,
                 policy_recommendations: list, executive_directive_text: str):
        super().__init__(
            alert_status_label=alert_status_label,
            alert_color_code=alert_color_code,
            school_name=school_name,
            state=state,
            enforcement_actions=enforcement_actions,
            policy_recommendations=policy_recommendations,
            executive_directive_text=executive_directive_text,
        )


def run(payload_school_id: str, source_system_name: str,
        agent_a: dict, agent_b: dict) -> dict[str, Any]:
    """
    Agent C: Generate executive brief with enforcement actions and policy recommendations.

    Combines Agent A (semantic analysis) + Agent B (discrepancy calculation)
    to produce actionable intelligence.

    Returns AgentCResult dict.
    """
    di_class = agent_b.get("di_classification", "DATA ALIGNED")
    flags = agent_b.get("flags", [])
    anomaly = agent_b.get("anomaly_detected", False)
    audit_snapshot = agent_b.get("audit_data_snapshot", {})
    severity = agent_a.get("severity", "LOW")
    category = agent_a.get("mapped_category", "General")

    school_name = audit_snapshot.get("school_name", "UNKNOWN")
    state = audit_snapshot.get("state", "UNKNOWN")

    # Alert determination
    if di_class in ("EXTREME DISCREPANCY", "SEVERE DISCREPANCY") or anomaly:
        alert_status_label = "TINDAKAN SEGERA DIPERLUKAN"
        alert_color_code = "#C62828"
    elif di_class == "MODERATE DISCREPANCY":
        alert_status_label = "PERHATIAN DIPERLUKAN"
        alert_color_code = "#F9AB00"
    elif di_class == "MINOR DISCREPANCY":
        alert_status_label = "PEMANTAUAN BERKALA"
        alert_color_code = "#003399"
    else:
        alert_status_label = "DATA SELARAS"
        alert_color_code = "#1E8E3E"

    # Enforcement actions based on category + severity
    enforcement_actions = []
    policy_recommendations = []

    if di_class in ("EXTREME DISCREPANCY", "SEVERE DISCREPANCY"):
        enforcement_actions.extend([
            "SIASATAN LANJUT oleh Pegawai Jemaah Nazir dalam tempoh 14 hari bekerja",
            "AUDIT MENGEJUT ke sekolah dalam tempoh 30 hari",
            "LAPORAN PENUH kepada Ketua Nazir Sekolah",
        ])
    elif di_class == "MODERATE DISCREPANCY":
        enforcement_actions.extend([
            "PEMANTAUAN BERJADUAL oleh PPD dalam tempoh 30 hari",
            "SEMAKAN DOKUMEN sokongan dari pihak sekolah",
        ])
    else:
        enforcement_actions.append("PEMANTAUAN RUTIN mengikut jadual sedia ada")

    if "HIGH_INTEGRITY_RISK_MATCH" in flags:
        enforcement_actions.append("RUJUKAN kepada Unit Integriti KPM")
        policy_recommendations.append("Melaksanakan Audit Integriti menyeluruh")

    if "SUSPICIOUS_HIGH_SCORE" in flags:
        enforcement_actions.append("VERIFIKASI DATA oleh Unit Nazir Negeri")
        policy_recommendations.append("Menyemak semula mekanisme pelaporan data sekolah")

    if "CRITICAL_LOW_SCORE" in flags:
        enforcement_actions.append("INTERVENSI KECEMASAN — Lawatan Nazir dalam 7 hari")
        policy_recommendations.append("Program Pemulihan Khas untuk sekolah terlibat")

    # Category-specific recommendations
    cat_recommendations = {
        "Facilities": ["Pemeriksaan infrastruktur fizikal", "Peruntukan khas pembaikan kecemasan"],
        "Academic Quality": ["Program intervensi akademik", "Penempatan guru pakar"],
        "Discipline": ["Program pemantapan disiplin pelajar", "Kerjasama dengan PDRM/AGC"],
        "Administrative Misconduct": ["Siasatan dalaman pentadbiran", "Laporan kepada SPRM jika perlu"],
    }
    if category in cat_recommendations:
        policy_recommendations.extend(cat_recommendations[category])

    # Executive directive
    executive_directive_text = f"""
EXECUTIVE DIRECTIVE — JN RESOLUSI
═══════════════════════════════════════
SEKOLAH: {school_name} ({state})
SUMBER: {source_system_name}
KATEGORI: {category} | SEVERITI: {severity}
STATUS: {alert_status_label}
DISCREPANCY INDEX: {agent_b.get('discrepancy_index', 0):.4f}
ANOMALI DIKESAN: {'YA' if anomaly else 'TIDAK'}

TINDAKAN:
{chr(10).join(f'  • {a}' for a in enforcement_actions)}

SYOR POLISI:
{chr(10).join(f'  • {p}' for p in policy_recommendations)}
═══════════════════════════════════════
Dokumen ini dijana automatik oleh JN Resolusi Engine.
"""

    result = AgentCResult(
        alert_status_label=alert_status_label,
        alert_color_code=alert_color_code,
        school_name=school_name,
        state=state,
        enforcement_actions=enforcement_actions,
        policy_recommendations=policy_recommendations,
        executive_directive_text=executive_directive_text,
    )
    return dict(result)
