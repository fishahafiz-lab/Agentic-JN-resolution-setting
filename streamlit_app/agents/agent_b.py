"""Agent B — Discrepancy Index & Anomaly Detection"""
import json
import uuid
from datetime import datetime
from typing import Any


class AgentBResult(dict):
    def __init__(self, case_id: str, discrepancy_index: float, di_classification: str,
                 flags: list, anomaly_detected: bool, confidence_score: float,
                 audit_data_snapshot: dict, score_delta: float):
        super().__init__(
            case_id=case_id,
            discrepancy_index=discrepancy_index,
            di_classification=di_classification,
            flags=flags,
            anomaly_detected=anomaly_detected,
            confidence_score=confidence_score,
            audit_data_snapshot=audit_data_snapshot,
            score_delta=score_delta,
        )


def _classify_di(di: float) -> str:
    if di >= 0.75:
        return "EXTREME DISCREPANCY"
    elif di >= 0.50:
        return "SEVERE DISCREPANCY"
    elif di >= 0.25:
        return "MODERATE DISCREPANCY"
    elif di >= 0.10:
        return "MINOR DISCREPANCY"
    return "DATA ALIGNED"


def run(school_id: str, operational_score: float, agent_a_result: dict,
        source_system_id: str) -> dict[str, Any]:
    """
    Agent B: Compare operational score against JN audit reference.
    Calculates Discrepancy Index and detects anomalies.

    Returns AgentBResult dict.
    """
    from database import JNDatabase

    db = JNDatabase()
    audit = db.get_audit_record(school_id)

    if not audit:
        audit = db.get_unknown_fallback()

    audit_score = audit.get("skpmg2_score", 50.0)

    # Calculate DI
    score_delta = round(abs(audit_score - operational_score), 2)
    discrepancy_index = round(score_delta / 100.0, 4)
    di_classification = _classify_di(discrepancy_index)

    # Anomaly detection
    flags = []
    anomaly_detected = False

    if discrepancy_index >= 0.50:
        flags.append("HIGH_DISCREPANCY")
        anomaly_detected = True

    if operational_score > 95 and audit_score < 70:
        flags.append("SUSPICIOUS_HIGH_SCORE")
        anomaly_detected = True

    if operational_score < 30:
        flags.append("CRITICAL_LOW_SCORE")
        anomaly_detected = True

    integrity_risk = audit.get("integrity_risk_index", 0.5)
    if integrity_risk > 0.6 and discrepancy_index > 0.3:
        flags.append("HIGH_INTEGRITY_RISK_MATCH")
        anomaly_detected = True

    # Confidence score
    base_confidence = 0.85
    if not audit or audit.get("school_id") == "UNKNOWN99":
        base_confidence = 0.55
    confidence_score = round(base_confidence - (len(flags) * 0.05), 2)
    confidence_score = max(0.3, min(0.98, confidence_score))

    # Case ID
    today = datetime.now().strftime("%Y%m%d")
    case_id = f"PRESTIJ-{today}-{str(uuid.uuid4())[:8].upper()}"

    result = AgentBResult(
        case_id=case_id,
        discrepancy_index=discrepancy_index,
        di_classification=di_classification,
        flags=flags,
        anomaly_detected=anomaly_detected,
        confidence_score=confidence_score,
        audit_data_snapshot={
            "audit_score": audit_score,
            "school_name": audit.get("school_name", "UNKNOWN"),
            "state": audit.get("state", "UNKNOWN"),
            "facility_gred": audit.get("facility_gred", "UNKNOWN"),
            "integrity_risk_index": audit.get("integrity_risk_index", 0.5),
        },
        score_delta=score_delta,
    )
    return dict(result)
