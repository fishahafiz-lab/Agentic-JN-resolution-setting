"""
JN Engine — Database Abstraction Layer
Neon PostgreSQL (Production) + SQLite (Local Dev)
Auto-detects DATABASE_URL from st.secrets or environment.
"""
import os
import uuid
import sqlite3
from datetime import datetime


def _db_url() -> str:
    """Get DATABASE_URL from Streamlit secrets or environment."""
    try:
        import streamlit as st
        return st.secrets.get("DATABASE_URL") or os.environ.get("DATABASE_URL", "")
    except Exception:
        return os.environ.get("DATABASE_URL", "")


def _gen_id() -> str:
    return str(uuid.uuid4())


class _Row(dict):
    """Dict with integer-index access for COUNT(*) fetchone()[0]."""
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class JNDatabase:
    """
    Unified DB wrapper.
    - PostgreSQL (Neon): fresh connection per query — serverless-safe.
    - SQLite: single persistent connection (local dev).
    """

    def __init__(self):
        url = _db_url()
        if url:
            self._url = url
            self._backend = "postgres"
            self._conn = None
        else:
            self._url = ""
            self._backend = "sqlite"
            db_dir = os.path.join(os.path.expanduser("~"), ".jn_engine")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "jn_engine.db")
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")

    @property
    def backend(self) -> str:
        return self._backend

    # ------------------------------------------------------------------
    # SQL translation
    # ------------------------------------------------------------------
    def _pg_connect(self):
        import psycopg2
        return psycopg2.connect(self._url)

    def _sql(self, sql: str) -> str:
        """Convert SQLite-style SQL to PostgreSQL."""
        if self._backend == "sqlite":
            return sql
        sql = sql.replace("?", "%s")
        sql = sql.replace("datetime('now')", "NOW()")
        return sql

    def _exec(self, sql: str, params=(), fetch: bool = True):
        """Execute SQL. Returns list of _Row dicts."""
        if self._backend == "postgres":
            conn = self._pg_connect()
            try:
                cur = conn.cursor()
                cur.execute(self._sql(sql), params)
                if fetch and cur.description:
                    cols = [d[0] for d in cur.description]
                    rows = [_Row(zip(cols, r)) for r in cur.fetchall()]
                else:
                    rows = []
                conn.commit()
                return rows
            finally:
                conn.close()
        else:
            cur = self._conn.execute(sql, params)
            if fetch and cur.description:
                cols = [d[0] for d in cur.description]
                return [_Row(zip(cols, r)) for r in cur.fetchall()]
            self._conn.commit()
            return []

    def _exec_one(self, sql: str, params=()):
        rows = self._exec(sql, params)
        return rows[0] if rows else None

    # ------------------------------------------------------------------
    # Schema initialization
    # ------------------------------------------------------------------
    def init_schema(self):
        """Create all tables if they don't exist. Idempotent."""
        self._exec("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'peneraju_sektor',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """, fetch=False)

        self._exec("""
            CREATE TABLE IF NOT EXISTS jn_audit_records (
                school_id TEXT PRIMARY KEY,
                school_name TEXT NOT NULL,
                school_type TEXT,
                district TEXT,
                state TEXT,
                last_audit_date TEXT,
                skpmg2_score REAL,
                facility_gred TEXT,
                canteen_hygiene_score REAL,
                integrity_risk_index REAL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """, fetch=False)

        self._exec("""
            CREATE TABLE IF NOT EXISTS matrix_payloads (
                id TEXT PRIMARY KEY,
                source_system_id TEXT,
                source_system_name TEXT,
                source_version TEXT,
                school_id TEXT,
                raw_text_extracted TEXT,
                operational_score REAL,
                mapped_category TEXT,
                severity_level TEXT,
                extracted_entities TEXT,
                received_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """, fetch=False)

        self._exec("""
            CREATE TABLE IF NOT EXISTS discrepancy_log (
                id TEXT PRIMARY KEY,
                case_id TEXT UNIQUE NOT NULL,
                school_id TEXT,
                school_name TEXT,
                state TEXT,
                source_system_name TEXT,
                audit_score_reference REAL,
                operational_score_reported REAL,
                score_delta REAL,
                discrepancy_index REAL,
                di_classification TEXT,
                flags TEXT,
                anomaly_detected INTEGER DEFAULT 0,
                confidence_score REAL,
                agent_a_result TEXT,
                agent_c_result TEXT,
                brief_content TEXT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """, fetch=False)

    # ------------------------------------------------------------------
    # Seed data
    # ------------------------------------------------------------------
    def seed_audit_records(self):
        """Insert 7 JN audit reference schools (idempotent)."""
        records = [
            ("SBP001", "SBP Integrasi Gombak", "SBP", "Gombak", "Selangor", "2024-06-15", 88.5, "A", 92.0, 0.12),
            ("SMK002", "SMK Putrajaya Presint 9", "SMK Harian", "Putrajaya", "WP Putrajaya", "2024-05-20", 76.0, "B", 78.5, 0.35),
            ("SMK003", "SMK King George V", "SMK Harian", "Seremban", "Negeri Sembilan", "2024-04-10", 82.3, "A", 85.0, 0.22),
            ("SABK004", "SABK Maahad Tahfiz Al-Amin", "SABK", "Kota Bharu", "Kelantan", "2024-03-28", 65.7, "C", 60.0, 0.48),
            ("SMK005", "SMK St. Michael", "SMK Harian", "Ipoh", "Perak", "2024-07-01", 79.1, "B", 81.0, 0.28),
            ("SBP006", "SBP Integrasi Rawang", "SBP", "Gombak", "Selangor", "2024-02-14", 91.2, "A", 94.5, 0.08),
            ("SMK007", "SMK Taman Tun Aminah", "SMK Harian", "Johor Bahru", "Johor", "2024-06-30", 72.4, "B", 74.0, 0.40),
        ]
        sql = """
            INSERT OR IGNORE INTO jn_audit_records
            (school_id, school_name, school_type, district, state, last_audit_date,
             skpmg2_score, facility_gred, canteen_hygiene_score, integrity_risk_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for r in records:
            self._exec(sql, r, fetch=False)

    def seed_admin_user(self):
        """Create default admin if no users exist."""
        from passlib.context import CryptContext
        pwd = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
        existing = self._exec_one("SELECT COUNT(*) AS cnt FROM users")
        if existing and existing["cnt"] == 0:
            self._exec("""
                INSERT INTO users (id, email, password_hash, role, is_active, created_at)
                VALUES (?, ?, ?, 'admin', 1, datetime('now'))
            """, (_gen_id(), "admin@moe.gov.my", pwd.hash("admin1234")), fetch=False)

    # ------------------------------------------------------------------
    # Auth queries
    # ------------------------------------------------------------------
    def get_user_by_email(self, email: str):
        return self._exec_one("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))

    def create_user(self, email: str, password_hash: str, role: str):
        uid = _gen_id()
        self._exec("""
            INSERT INTO users (id, email, password_hash, role, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, datetime('now'))
        """, (uid, email, password_hash, role), fetch=False)
        return uid

    def list_users(self):
        return self._exec("SELECT id, email, role, is_active, created_at FROM users ORDER BY created_at DESC")

    def delete_user(self, user_id: str):
        self._exec("DELETE FROM users WHERE id = ?", (user_id,), fetch=False)

    # ------------------------------------------------------------------
    # Matrix payload queries
    # ------------------------------------------------------------------
    def insert_payload(self, payload: dict):
        self._exec("""
            INSERT INTO matrix_payloads
            (id, source_system_id, source_system_name, source_version, school_id,
             raw_text_extracted, operational_score, mapped_category, severity_level,
             extracted_entities, received_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            payload["id"], payload["source_system_id"], payload["source_system_name"],
            payload.get("source_version", ""), payload["school_id"],
            payload["raw_text_extracted"], payload["operational_score"],
            payload.get("mapped_category", ""), payload.get("severity_level", ""),
            payload.get("extracted_entities", ""),
        ), fetch=False)

    def get_payloads(self, limit: int = 100):
        return self._exec("SELECT * FROM matrix_payloads ORDER BY received_at DESC LIMIT ?", (limit,))

    # ------------------------------------------------------------------
    # Discrepancy log queries
    # ------------------------------------------------------------------
    def insert_discrepancy(self, d: dict):
        self._exec("""
            INSERT INTO discrepancy_log
            (id, case_id, school_id, school_name, state, source_system_name,
             audit_score_reference, operational_score_reported, score_delta,
             discrepancy_index, di_classification, flags, anomaly_detected,
             confidence_score, agent_a_result, agent_c_result, brief_content, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            d["id"], d["case_id"], d["school_id"], d["school_name"], d["state"],
            d["source_system_name"], d["audit_score_reference"], d["operational_score_reported"],
            d["score_delta"], d["discrepancy_index"], d["di_classification"],
            d.get("flags", "[]"), d.get("anomaly_detected", 0), d.get("confidence_score", 0.0),
            d.get("agent_a_result", "{}"), d.get("agent_c_result", "{}"), d.get("brief_content", "{}"),
        ), fetch=False)

    def get_cases(self, limit: int = 100):
        return self._exec("""
            SELECT * FROM discrepancy_log ORDER BY timestamp DESC LIMIT ?
        """, (limit,))

    def get_case_by_id(self, case_id: str):
        return self._exec_one("SELECT * FROM discrepancy_log WHERE case_id = ?", (case_id,))

    def get_case_count(self):
        row = self._exec_one("SELECT COUNT(*) AS cnt FROM discrepancy_log")
        return row["cnt"] if row else 0

    def get_di_summary(self):
        """Return DI distribution for dashboard."""
        rows = self._exec("""
            SELECT di_classification, COUNT(*) as cnt FROM discrepancy_log GROUP BY di_classification
        """)
        return {r["di_classification"]: r["cnt"] for r in rows} if rows else {}

    def get_avg_di(self):
        row = self._exec_one("SELECT AVG(discrepancy_index) AS avg_di FROM discrepancy_log")
        return round(row["avg_di"], 4) if row and row["avg_di"] else 0.0

    # ------------------------------------------------------------------
    # Audit reference queries
    # ------------------------------------------------------------------
    def get_audit_record(self, school_id: str):
        return self._exec_one("SELECT * FROM jn_audit_records WHERE school_id = ?", (school_id,))

    def get_unknown_fallback(self):
        return {
            "school_id": "UNKNOWN99", "school_name": "UNKNOWN",
            "school_type": "UNKNOWN", "district": "UNKNOWN", "state": "UNKNOWN",
            "last_audit_date": "", "skpmg2_score": 50.0, "facility_gred": "C",
            "canteen_hygiene_score": 50.0, "integrity_risk_index": 0.50, "created_at": "",
        }
