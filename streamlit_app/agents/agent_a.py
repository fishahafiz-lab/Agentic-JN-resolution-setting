"""Agent A — Semantic Ingestion & Category Mapping"""
from typing import Any


class AgentAResult(dict):
    """Structured result from Agent A."""
    def __init__(self, mapped_category: str, category_confidence: float,
                 severity: str, severity_confidence: float,
                 extracted_entities: list, processing_notes: str):
        super().__init__(
            mapped_category=mapped_category,
            category_confidence=category_confidence,
            severity=severity,
            severity_confidence=severity_confidence,
            extracted_entities=extracted_entities,
            processing_notes=processing_notes,
        )


# Category keyword map
CATEGORY_MAP = {
    "Facilities": ["bangunan", "kelas", "tandas", "bilik", "padang", "makmal", "bengkel",
                   "perpustakaan", "surau", "kantin", "pagar", "bumbung", "dinding", "lantai",
                   "facility", "building", "roof", "toilet", "classroom", "lab", "canteen"],
    "Academic Quality": ["akademik", "peperiksaan", "spm", "pt3", "gred", "markah", "lulus",
                         "gagal", "subjek", "guru", "mengajar", "kurikulum", "sukatan",
                         "academic", "exam", "grade", "curriculum", "teacher"],
    "Discipline": ["disiplin", "ponteng", "buli", "gangguan", "salah laku", "merokok",
                   "vape", "pergaduhan", "discipline", "bully", "absenteeism", "truancy"],
    "Administrative Misconduct": ["kewangan", "peruntukan", "tender", "penyelewengan",
                                  "salah guna", "kuasa", "dokumen", "palsu", "rasuah",
                                  "finance", "corruption", "fraud", "misconduct", "abuse"],
}


def run(school_id: str, raw_text: str, source_system_id: str) -> dict[str, Any]:
    """
    Agent A: Analyze raw complaint/payload text and extract semantic meaning.

    Args:
        school_id: School identifier
        raw_text: Raw text from the source system
        source_system_id: ID of the originating system

    Returns:
        AgentAResult with mapped_category, severity, extracted_entities
    """
    import json

    text_lower = raw_text.lower()
    category_scores = {}

    for category, keywords in CATEGORY_MAP.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            category_scores[category] = score

    if not category_scores:
        mapped_category = "General Complaint"
        category_confidence = 0.5
    else:
        mapped_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[mapped_category]
        total_score = sum(category_scores.values())
        category_confidence = min(0.95, max(0.5, max_score / max(total_score, 1)))

    # Severity detection
    severity_keywords_high = ["kritikal", "bahaya", "segera", "kecemasan", "maut", "kemalangan",
                              "critical", "danger", "emergency", "fatal", "severe", "rosak teruk"]
    severity_keywords_moderate = ["sederhana", "perlu perhatian", "rosak", "tidak selesa",
                                  "moderate", "damaged", "uncomfortable"]
    severity_keywords_low = ["kecil", "ringan", "minor", "cadangan", "suggestion", "minor"]

    high_count = sum(1 for kw in severity_keywords_high if kw in text_lower)
    mod_count = sum(1 for kw in severity_keywords_moderate if kw in text_lower)
    low_count = sum(1 for kw in severity_keywords_low if kw in text_lower)

    total_sev = high_count * 3 + mod_count * 2 + low_count * 1
    if total_sev >= 6:
        severity = "HIGH"
        severity_confidence = min(0.95, 0.6 + total_sev * 0.05)
    elif total_sev >= 3:
        severity = "MEDIUM"
        severity_confidence = 0.6 + total_sev * 0.05
    else:
        severity = "LOW"
        severity_confidence = 0.5 + total_sev * 0.1

    # Entity extraction (simple NER-style)
    entities = []
    # School name patterns
    import re
    school_patterns = [
        r'(?:SMK|SBP|SABK|SMJK|SK|SJK[TK])\s+[A-Za-z\s]+',
        r'Sekolah\s+(?:Menengah|Kebangsaan|Rendah)\s+[A-Za-z\s]+',
    ]
    for pat in school_patterns:
        matches = re.findall(pat, raw_text, re.IGNORECASE)
        for m in matches:
            entities.append({"type": "SCHOOL", "value": m.strip()})

    # Amount/currency
    amt_matches = re.findall(r'RM\s*\d[\d,.]*', raw_text)
    for m in amt_matches:
        entities.append({"type": "AMOUNT", "value": m})

    processing_notes = (
        f"Category mapping: {mapped_category} (confidence: {category_confidence:.2f}). "
        f"Severity: {severity} (confidence: {severity_confidence:.2f}). "
        f"Extracted {len(entities)} entities."
    )

    result = AgentAResult(
        mapped_category=mapped_category,
        category_confidence=round(category_confidence, 4),
        severity=severity,
        severity_confidence=round(severity_confidence, 4),
        extracted_entities=entities,
        processing_notes=processing_notes,
    )
    return dict(result)
