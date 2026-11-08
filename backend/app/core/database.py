import sqlite3
import json
import time
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.core.security import hash_password
from backend.app.models.schemas.transaction import EnrichedTransaction
from backend.app.models.schemas.rule import DetectionRule
from backend.app.models.schemas.alert import Alert

def get_email_avatar_url(email: str) -> str:
    """
    Standardized email profile picture URL generator.
    Queries public avatar providers (Google Workspace, Gravatar, GitHub)
    and falls back to 404 so UI can render the user's first capital letter.
    """
    clean = (email or "").strip().lower()
    if not clean or "@" not in clean:
        return ""
    md5_hash = hashlib.md5(clean.encode("utf-8")).hexdigest()
    return f"https://unavatar.io/{clean}?fallback=https%3A%2F%2Fwww.gravatar.com%2Favatar%2F{md5_hash}%3Fd%3D404"

class Database:
    def __init__(self, db_path: str = settings.DB_PATH):
        self.db_path = db_path
        self._metrics_cache: Dict[Tuple[str, str, str, str], Tuple[float, Dict[str, Any]]] = {}
        self._activity_cache: Dict[Tuple[str, str, str, str], Tuple[float, Dict[str, Any]]] = {}
        self._max_ts_cache: Tuple[float, float] = (0.0, 0.0)
        self._known_cities: Dict[str, str] = {}
        self._known_states: Dict[str, str] = {}
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    def _load_geo_lookups(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT city FROM transactions WHERE city IS NOT NULL AND city != ''")
                for r in cursor.fetchall():
                    c = r[0].strip()
                    self._known_cities[c.lower()] = c
                cursor.execute("SELECT DISTINCT state FROM transactions WHERE state IS NOT NULL AND state != ''")
                for r in cursor.fetchall():
                    s = r[0].strip()
                    self._known_states[s.lower()] = s
        except Exception:
            pass

    def _get_max_timestamp(self, conn: sqlite3.Connection) -> float:
        now = time.time()
        if now - self._max_ts_cache[0] < 10.0 and self._max_ts_cache[1] > 0:
            return self._max_ts_cache[1]
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM transactions")
        row = cursor.fetchone()
        max_ts = row[0] if row and row[0] else now
        self._max_ts_cache = (now, max_ts)
        return max_ts

    def _apply_geo_filter(self, val: Optional[str], conditions: List[str], params: List[Any]):
        if not val or val.strip().upper() == "ALL":
            return
        v_clean = val.strip()
        v_lower = v_clean.lower()
        if not self._known_cities or not self._known_states:
            self._load_geo_lookups()

        if v_lower in self._known_cities:
            canonical = self._known_cities[v_lower]
            conditions.append("city = ?")
            params.append(canonical)
        elif v_lower in self._known_states:
            canonical = self._known_states[v_lower]
            conditions.append("state = ?")
            params.append(canonical)
        else:
            conditions.append("(state = ? OR city = ?)")
            params.extend([v_clean, v_clean])

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # High-performance WAL mode and memory cache
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA cache_size = -64000")
            cursor.execute("PRAGMA temp_store = MEMORY")

            # Transactions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                user_id TEXT,
                card_id TEXT,
                amount REAL,
                currency TEXT,
                merchant TEXT,
                merchant_category TEXT,
                channel TEXT,
                device_id TEXT,
                ip_address TEXT,
                lat REAL,
                lon REAL,
                city TEXT,
                country TEXT,
                status TEXT,
                risk_score REAL,
                risk_level TEXT,
                triggered_rules TEXT,
                reason_summary TEXT,
                latency_ms REAL,
                full_json TEXT
            )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_time ON transactions(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_user ON transactions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_status ON transactions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_score ON transactions(risk_score DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_country_time ON transactions(country, timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_country_city ON transactions(country, city, timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_country_state ON transactions(country, state, timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_country_status ON transactions(country, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_city_status ON transactions(city, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_metrics_all ON transactions(timestamp DESC, status, amount, latency_ms)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_metrics_country ON transactions(country, timestamp DESC, status, amount, latency_ms)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_metrics_city ON transactions(country, city, timestamp DESC, status, amount, latency_ms)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_metrics_state ON transactions(country, state, timestamp DESC, status, amount, latency_ms)")

            # Migration: Ensure state, payment_method, payment_rail, upi_id columns exist
            for col, dtype in [("state", "TEXT"), ("payment_method", "TEXT DEFAULT 'CARD'"), ("payment_rail", "TEXT DEFAULT 'VISA'"), ("upi_id", "TEXT")]:
                try:
                    cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col} {dtype}")
                except sqlite3.OperationalError:
                    pass

            # Rules table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                category TEXT,
                condition_code TEXT,
                threshold REAL,
                weight REAL,
                action TEXT,
                enabled INTEGER
            )
            """)

            # Alerts table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                transaction_id TEXT,
                timestamp REAL,
                user_id TEXT,
                amount REAL,
                currency TEXT,
                merchant TEXT,
                risk_score REAL,
                risk_level TEXT,
                status TEXT,
                triggered_rules TEXT,
                reason_summary TEXT,
                analyst_notes TEXT,
                resolved_by TEXT,
                resolved_at REAL
            )
            """)

            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                profile_picture_url TEXT,
                role TEXT DEFAULT 'Lead Risk Officer',
                organization TEXT DEFAULT 'FinSecure Inc.',
                clearance TEXT DEFAULT 'SuperAdmin • Level 4',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

            # Audit logs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                action TEXT,
                actor TEXT,
                target TEXT,
                status TEXT,
                details TEXT,
                ip_address TEXT DEFAULT '127.0.0.1',
                user_agent TEXT DEFAULT 'Web Browser',
                clearance TEXT DEFAULT 'Level 4'
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_logs(timestamp DESC)")

            # Password reset tokens table (real email dispatch & verification)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                code TEXT NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                used_at REAL DEFAULT NULL,
                ip_address TEXT,
                user_agent TEXT
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reset_token ON password_resets(token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reset_code ON password_resets(code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reset_email ON password_resets(email)")

            # Migration: Ensure audit_logs columns exist for Level 4 Authority tracking
            for col, dtype in [
                ("ip_address", "TEXT DEFAULT '127.0.0.1'"),
                ("user_agent", "TEXT DEFAULT 'Web Browser'"),
                ("clearance", "TEXT DEFAULT 'Level 4'")
            ]:
                try:
                    cursor.execute(f"ALTER TABLE audit_logs ADD COLUMN {col} {dtype}")
                except sqlite3.OperationalError:
                    pass

            # Seed default detection rules if table is empty
            cursor.execute("SELECT COUNT(*) FROM rules")
            if cursor.fetchone()[0] == 0:
                self._seed_default_rules(cursor)

            # Seed default users if table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self._seed_default_users(cursor)

            # Migration: Ensure existing users' avatars are updated to email profile picture format
            try:
                cursor.execute("SELECT id, email FROM users WHERE profile_picture_url LIKE '%unsplash.com%' OR profile_picture_url IS NULL")
                legacy_rows = cursor.fetchall()
                for r in legacy_rows:
                    uid = r["id"]
                    em = (r["email"] or "").strip().lower()
                    if em:
                        new_avatar = get_email_avatar_url(em)
                        cursor.execute("UPDATE users SET profile_picture_url = ? WHERE id = ?", (new_avatar, uid))
            except Exception:
                pass

            conn.commit()

    def _seed_default_rules(self, cursor: sqlite3.Cursor):
        default_rules = [
            (
                "RULE_GEO_VELOCITY",
                "Impossible Travel Speed (>800 km/h)",
                "Detects subsequent transactions across geographic distances impossible for human flight",
                "GEO_DISTANCE",
                "geo_speed_kmh > 800",
                800.0,
                38.0,
                "BLOCK",
                1
            ),
            (
                "RULE_BURST_VELOCITY",
                "High Frequency Burst (>3 tx / 60 sec)",
                "Triggers when an account attempts 4+ transactions within a 60 second window",
                "VELOCITY",
                "tx_count_60s >= 4",
                4.0,
                32.0,
                "FLAG",
                1
            ),
            (
                "RULE_CARDING_MICRO_PROBE",
                "Carding Micro-Probe (<$3.00 probe then large jump)",
                "Identifies automated bots testing stolen cards with small charges before massive payout",
                "AMOUNT_SPIKE",
                "has_micro_probe_prior and amount > 500",
                500.0,
                35.0,
                "BLOCK",
                1
            ),
            (
                "RULE_VPN_TOR_ANONYMIZER",
                "Known Anonymizer / TOR Exit Node Access",
                "Flags transactions originating from TOR exits or commercial VPN proxy infrastructure",
                "DEVICE_IP",
                "is_vpn_tor == True",
                1.0,
                22.0,
                "FLAG",
                1
            ),
            (
                "RULE_HIGH_RISK_MCC",
                "High-Risk Offshore / Crypto Merchant",
                "Enhanced scrutiny for unverified crypto on-ramps and offshore casino gateways",
                "MCC_RESTRICTION",
                "merchant_category in ['CRYPTO_EXCHANGE', 'GAMBLING'] and amount > 1500",
                1500.0,
                28.0,
                "FLAG",
                1
            ),
            (
                "RULE_AMOUNT_Z_SCORE",
                "Extreme Statistical Amount Outlier (Z > 3.5)",
                "Transaction amount exceeds 3.5 standard deviations from user's 90-day moving average",
                "AMOUNT_SPIKE",
                "amount_z_score > 3.5",
                3.5,
                25.0,
                "FLAG",
                1
            ),
            (
                "RULE_MULE_GRAPH_CLUSTER",
                "Shared Entity Fraud Ring Linkage",
                "Account shares device fingerprint or IP subnet with 3+ distinct active accounts",
                "DEVICE_IP",
                "graph_shared_entities >= 3",
                3.0,
                40.0,
                "BLOCK",
                1
            ),
            (
                "RULE_UPI_COLLECT_SCAM",
                "UPI Phishing / Unauthorized Collect Scam",
                "Detects suspicious high-value UPI collect requests or unauthorized VPA mandate spikes",
                "PAYMENT_METHOD",
                "payment_method == 'UPI' and amount > 1200",
                1200.0,
                42.0,
                "BLOCK",
                1
            )
        ]
        cursor.executemany(
            "INSERT INTO rules VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            default_rules
        )

    def _seed_default_users(self, cursor: sqlite3.Cursor):
        default_users = [
            (
                "Alexander Vance",
                "admin@finsecure.io",
                hash_password("admin2026"),
                get_email_avatar_url("admin@finsecure.io"),
                "Lead Risk Officer",
                "FinSecure Inc.",
                "SuperAdmin • Level 4"
            ),
            (
                "Sarah Chen",
                "sarah.chen@finsecure.io",
                hash_password("sarah2026"),
                get_email_avatar_url("sarah.chen@finsecure.io"),
                "Senior Threat Hunter",
                "FinSecure Inc.",
                "Level 3: Senior Risk Officer"
            ),
            (
                "Marcus Reid",
                "marcus.reid@finsecure.io",
                hash_password("marcus2026"),
                get_email_avatar_url("marcus.reid@finsecure.io"),
                "SOC Operations Lead",
                "FinSecure Inc.",
                "Level 2: SOC Incident Responder"
            )
        ]
        cursor.executemany(
            "INSERT INTO users (name, email, password_hash, profile_picture_url, role, organization, clearance) VALUES (?, ?, ?, ?, ?, ?, ?)",
            default_users
        )

    def insert_transaction(self, enriched: EnrichedTransaction):
        tx = enriched.transaction
        dec = enriched.decision
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO transactions (
                id, timestamp, user_id, card_id, amount, currency, merchant,
                merchant_category, channel, device_id, ip_address, lat, lon,
                city, state, country, status, risk_score, risk_level, triggered_rules,
                reason_summary, latency_ms, full_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tx.id, tx.timestamp, tx.user_id, tx.card_id, tx.amount, tx.currency,
                tx.merchant, tx.merchant_category, tx.channel, tx.device_id, tx.ip_address,
                tx.location.lat, tx.location.lon, tx.location.city, getattr(tx.location, "state", ""), tx.location.country,
                dec.status, dec.risk_score, dec.risk_level,
                json.dumps(dec.triggered_rules), dec.reason_summary, dec.latency_ms,
                enriched.model_dump_json()
            ))

            # Auto-create alert if FLAGGED or BLOCKED
            if dec.status in ["FLAGGED", "BLOCKED"]:
                cursor.execute("""
                INSERT OR IGNORE INTO alerts (
                    id, transaction_id, timestamp, user_id, amount, currency,
                    merchant, risk_score, risk_level, status, triggered_rules,
                    reason_summary, analyst_notes, resolved_by, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"ALT-{tx.id[-8:]}", tx.id, tx.timestamp, tx.user_id, tx.amount, tx.currency,
                    tx.merchant, dec.risk_score, dec.risk_level, "NEW",
                    json.dumps(dec.triggered_rules), dec.reason_summary, None, None, None
                ))

            conn.commit()

    def _get_canonical_country(self, country: str) -> str:
        if not country:
            return country
        c = country.strip().upper()
        mapping = {
            "UNITED STATES": "United States", "USA": "United States", "US": "United States",
            "UNITED KINGDOM": "United Kingdom", "UK": "United Kingdom", "GB": "United Kingdom", "GBR": "United Kingdom",
            "UNITED ARAB EMIRATES": "United Arab Emirates", "UAE": "United Arab Emirates", "AE": "United Arab Emirates", "ARE": "United Arab Emirates",
            "INDIA": "India", "IND": "India", "IN": "India",
            "GERMANY": "Germany", "DEU": "Germany", "DE": "Germany",
            "JAPAN": "Japan", "JPN": "Japan", "JP": "Japan",
            "CANADA": "Canada", "CAN": "Canada", "CA": "Canada",
            "AUSTRALIA": "Australia", "AUS": "Australia", "AU": "Australia",
            "BRAZIL": "Brazil", "BRA": "Brazil", "BR": "Brazil",
            "FRANCE": "France", "FRA": "France", "FR": "France",
            "SINGAPORE": "Singapore", "SGP": "Singapore", "SG": "Singapore"
        }
        return mapping.get(c, country.strip())

    def _get_country_aliases(self, country: str) -> List[str]:
        canon = self._get_canonical_country(country)
        return [canon]

    def get_recent_transactions(
        self,
        limit: int = 50,
        status_filter: Optional[str] = None,
        country_filter: Optional[str] = None,
        state_filter: Optional[str] = None,
        city_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            conditions: List[str] = []
            params: List[Any] = []
            if status_filter and status_filter.upper() != "ALL":
                sf = status_filter.upper()
                if sf in ("REVIEW", "FLAGGED", "UNDER_REVIEW"):
                    conditions.append("status IN ('FLAGGED', 'REVIEW')")
                else:
                    conditions.append("status = ?")
                    params.append(sf)
            if country_filter and country_filter.upper() != "ALL":
                canon_country = self._get_canonical_country(country_filter)
                conditions.append("country = ?")
                params.append(canon_country)
            if city_filter and city_filter.upper() != "ALL":
                self._apply_geo_filter(city_filter, conditions, params)
            if state_filter and state_filter.upper() != "ALL" and state_filter != city_filter:
                self._apply_geo_filter(state_filter, conditions, params)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            query = f"SELECT status, risk_score, full_json FROM transactions {where_clause} ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                col_status, col_score, full_json_str = r[0], r[1], r[2]
                item = json.loads(full_json_str) if full_json_str else {}
                if "decision" not in item:
                    item["decision"] = {}
                if col_status:
                    item["decision"]["status"] = col_status
                if col_score and col_score > 0:
                    item["decision"]["risk_score"] = round(float(col_score), 1)
                elif not item["decision"].get("risk_score") or item["decision"]["risk_score"] == 0:
                    item["decision"]["risk_score"] = 92.4 if col_status == "BLOCKED" else (61.8 if col_status == "FLAGGED" else 11.4)
                sc = item["decision"]["risk_score"]
                item["decision"]["risk_level"] = "CRITICAL" if sc >= 75 else ("MEDIUM" if sc >= 50 else "LOW")
                results.append(item)
            return results

    def get_distinct_countries(self) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT country FROM transactions WHERE country IS NOT NULL AND country != '' ORDER BY country ASC")
            rows = cursor.fetchall()
            return [r[0] for r in rows if r[0]]

    def get_distinct_states(self, country: Optional[str] = None) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if country and country.upper() != "ALL":
                cursor.execute(
                    "SELECT DISTINCT state FROM transactions WHERE state IS NOT NULL AND state != '' AND (country = ? OR UPPER(country) = ?) ORDER BY state ASC",
                    (country, country.upper())
                )
            else:
                cursor.execute(
                    "SELECT DISTINCT state FROM transactions WHERE state IS NOT NULL AND state != '' ORDER BY state ASC"
                )
            rows = cursor.fetchall()
            return [r[0] for r in rows if r[0]]

    def get_distinct_cities(self, country: Optional[str] = None) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if country and country.upper() != "ALL":
                aliases = self._get_country_aliases(country)
                placeholders = ",".join(["?"] * len(aliases))
                cursor.execute(
                    f"SELECT DISTINCT city FROM transactions WHERE city IS NOT NULL AND city != '' AND country IN ({placeholders}) ORDER BY city ASC",
                    tuple(aliases)
                )
            else:
                cursor.execute(
                    "SELECT DISTINCT city FROM transactions WHERE city IS NOT NULL AND city != '' ORDER BY city ASC"
                )
            rows = cursor.fetchall()
            return [r[0] for r in rows if r[0]]

    def get_transaction_by_id(self, tx_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT full_json FROM transactions WHERE id = ?", (tx_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def get_all_rules(self) -> List[DetectionRule]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rules")
            rows = cursor.fetchall()
            rules = []
            for r in rows:
                rules.append(DetectionRule(
                    id=r["id"],
                    name=r["name"],
                    description=r["description"],
                    category=r["category"],
                    condition_code=r["condition_code"],
                    threshold=float(r["threshold"]),
                    weight=float(r["weight"]),
                    action=r["action"],
                    enabled=bool(r["enabled"])
                ))
            return rules

    def update_rule(self, rule_id: str, enabled: Optional[bool] = None, threshold: Optional[float] = None, weight: Optional[float] = None, action: Optional[str] = None) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            updates: List[str] = []
            params: List[Any] = []
            if enabled is not None:
                updates.append("enabled = ?")
                params.append(1 if enabled else 0)
            if threshold is not None:
                updates.append("threshold = ?")
                params.append(threshold)
            if weight is not None:
                updates.append("weight = ?")
                params.append(weight)
            if action is not None:
                updates.append("action = ?")
                params.append(action)
            if not updates:
                return False
            params.append(rule_id)
            cursor.execute(f"UPDATE rules SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
            return cursor.rowcount > 0

    def get_alerts(self, limit: int = 50, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status_filter:
                cursor.execute(
                    "SELECT * FROM alerts WHERE status = ? ORDER BY timestamp DESC LIMIT ?",
                    (status_filter.upper(), limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            rows = cursor.fetchall()
            alerts = []
            for r in rows:
                alerts.append({
                    "id": r["id"],
                    "transaction_id": r["transaction_id"],
                    "timestamp": r["timestamp"],
                    "user_id": r["user_id"],
                    "amount": r["amount"],
                    "currency": r["currency"],
                    "merchant": r["merchant"],
                    "risk_score": r["risk_score"],
                    "risk_level": r["risk_level"],
                    "status": r["status"],
                    "triggered_rules": json.loads(r["triggered_rules"]) if r["triggered_rules"] else [],
                    "reason_summary": r["reason_summary"],
                    "analyst_notes": r["analyst_notes"],
                    "resolved_by": r["resolved_by"],
                    "resolved_at": r["resolved_at"]
                })
            return alerts

    def resolve_alert(self, alert_id: str, action: str, notes: str = "", analyst_id: str = "analyst_sec_ops") -> bool:
        status_map = {
            "APPROVE": "RESOLVED_LEGIT",
            "BLOCK": "RESOLVED_FRAUD",
            "ESCALATE": "UNDER_REVIEW",
            "REQUEST_KYC": "UNDER_REVIEW"
        }
        new_status = status_map.get(action.upper(), "RESOLVED_FRAUD")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE alerts
            SET status = ?, analyst_notes = ?, resolved_by = ?, resolved_at = ?
            WHERE id = ?
            """, (new_status, notes, analyst_id, time.time(), alert_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_metrics(
        self,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        timeframe: Optional[str] = None
    ) -> Dict[str, Any]:
        cache_key = (country or "ALL", state or "ALL", city or "ALL", timeframe or "30")
        now = time.time()
        if cache_key in self._metrics_cache:
            cached_time, cached_val = self._metrics_cache[cache_key]
            if now - cached_time < 5.0:
                return cached_val

        with self._get_connection() as conn:
            cursor = conn.cursor()
            conditions: List[str] = []
            params: List[Any] = []
            if country and country.upper() != "ALL":
                canon_country = self._get_canonical_country(country)
                conditions.append("country = ?")
                params.append(canon_country)

            # High-performance single-column index lookup for city or state
            if city and city.upper() != "ALL":
                self._apply_geo_filter(city, conditions, params)
            if state and state.upper() != "ALL" and state != city:
                self._apply_geo_filter(state, conditions, params)

            if timeframe and timeframe.upper() != "ALL":
                tf_str = timeframe.lower().strip()
                if tf_str in ["24", "24h", "1", "1d", "daily"]:
                    cutoff_span = 86400
                elif tf_str in ["7", "7d", "weekly"]:
                    cutoff_span = 7 * 86400
                else:  # 30 days
                    cutoff_span = 30 * 86400

                max_ts = self._get_max_timestamp(conn)
                cutoff = max_ts - cutoff_span
                conditions.append("timestamp >= ?")
                params.append(cutoff)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'FLAGGED' THEN 1 ELSE 0 END) as flagged,
                SUM(CASE WHEN status = 'BLOCKED' THEN 1 ELSE 0 END) as blocked,
                SUM(CASE WHEN status = 'BLOCKED' THEN amount ELSE 0 END) as prevented_loss,
                SUM(amount) as total_volume,
                AVG(latency_ms) as avg_latency
            FROM transactions
            {where_clause}
            """
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()

            total = row["total"] or 0
            approved = row["approved"] or 0
            flagged = row["flagged"] or 0
            blocked = row["blocked"] or 0
            prevented = row["prevented_loss"] or 0.0
            volume = row["total_volume"] or 0.0
            avg_lat = row["avg_latency"] or 0.0

            fraud_rate = ((flagged + blocked) / total * 100.0) if total > 0 else 0.0

            cursor.execute("SELECT COUNT(*) FROM rules WHERE enabled = 1")
            active_rules = cursor.fetchone()[0]

            donut_high = round((blocked / total) * 100, 1) if total > 0 else 18.0
            donut_med = round((flagged / total) * 100, 1) if total > 0 else 9.0
            donut_low = round(max(0.0, 100.0 - donut_high - donut_med), 1) if total > 0 else 73.0

            result = {
                "scope_country": country or "ALL",
                "scope_state": state or "ALL",
                "scope_city": city or "ALL",
                "timeframe": timeframe or "30",
                "total_transactions": total,
                "approved_count": approved,
                "flagged_count": flagged,
                "blocked_count": blocked,
                "fraud_count": blocked,
                "fraud_rate_pct": round(fraud_rate, 2),
                "prevented_loss_usd": round(prevented, 2),
                "total_volume_usd": round(volume, 2),
                "avg_latency_ms": round(avg_lat, 2),
                "active_rules_count": active_rules,
                "donut": {
                    "high": donut_high,
                    "med": donut_med,
                    "low": donut_low
                }
            }

            self._metrics_cache[cache_key] = (now, result)
            if len(self._metrics_cache) > 200:
                self._metrics_cache = {k: v for k, v in self._metrics_cache.items() if now - v[0] < 10.0}

            return result

    def get_activity_timeseries(
        self,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        timeframe: str = "Daily"
    ) -> Dict[str, Any]:
        target_loc = city or state
        tf = (timeframe or "Daily").strip().capitalize()
        cache_key = (country or "ALL", state or "ALL", city or "ALL", tf)
        now = time.time()
        if cache_key in self._activity_cache:
            cached_time, cached_val = self._activity_cache[cache_key]
            if now - cached_time < 5.0:
                return cached_val

        with self._get_connection() as conn:
            cursor = conn.cursor()
            conditions: List[str] = []
            params: List[Any] = []
            if country and country.upper() != "ALL":
                canon_country = self._get_canonical_country(country)
                conditions.append("country = ?")
                params.append(canon_country)
            if target_loc and target_loc.upper() != "ALL":
                self._apply_geo_filter(target_loc, conditions, params)

            max_ts = self._get_max_timestamp(conn)

            if tf == "Weekly":
                labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Today']
                num_points = 7
                span = 7 * 86400
                cutoff = max_ts - span
                interval = span / float(num_points)
                max_bucket = 6
            elif tf == "Monthly":
                labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Current']
                num_points = 5
                span = 30 * 86400
                cutoff = max_ts - span
                interval = span / float(num_points)
                max_bucket = 4
            else:  # Daily
                labels = ['12 AM', '4 AM', '8 AM', '12 PM', '4 PM', '8 PM', 'Now']
                num_points = 7
                span = 86400
                cutoff = max_ts - span
                interval = span / 7.0
                max_bucket = 6

            time_conds = list(conditions)
            time_params = [max_bucket, cutoff, interval, *params, cutoff]
            time_conds.append("timestamp >= ?")
            where_clause = f"WHERE {' AND '.join(time_conds)}"

            query = f"""
            SELECT 
                CAST(MIN(?, MAX(0, CAST((timestamp - ?) / ? AS INT))) AS INT) as bucket,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as legit,
                SUM(CASE WHEN status IN ('FLAGGED', 'BLOCKED') THEN 1 ELSE 0 END) as fraud
            FROM transactions
            {where_clause}
            GROUP BY bucket
            ORDER BY bucket
            """
            cursor.execute(query, tuple(time_params))
            bucket_rows = {row["bucket"]: row for row in cursor.fetchall()}

            legit_series: List[int] = []
            fraud_series: List[int] = []
            for b in range(num_points):
                if b in bucket_rows:
                    brow = bucket_rows[b]
                    legit_series.append(brow["legit"] or 0)
                    fraud_series.append(brow["fraud"] or 0)
                else:
                    legit_series.append(0)
                    fraud_series.append(0)

            total_legit = sum(legit_series)
            total_fraud = sum(fraud_series)
            total_tx = total_legit + total_fraud

            result = {
                "timeframe": tf,
                "labels": labels,
                "legitimate": legit_series,
                "fraudulent": fraud_series,
                "total_transactions": total_tx,
                "legit_total": total_legit,
                "fraud_total": total_fraud,
                "country": country or "ALL",
                "city": target_loc or "ALL"
            }

            self._activity_cache[cache_key] = (now, result)
            if len(self._activity_cache) > 120:
                self._activity_cache = {k: v for k, v in self._activity_cache.items() if now - v[0] < 5.0}

            return result

    # =========================================================================
    # User Authentication & Profile Repository (SQLite)
    # =========================================================================
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.strip().lower(),))
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)

    def get_all_users(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email, profile_picture_url, role, organization, clearance, created_at FROM users ORDER BY id ASC"
            )
            return [dict(r) for r in cursor.fetchall()]

    def update_user_avatar(self, user_id: int, avatar_url: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET profile_picture_url = ? WHERE id = ?", (avatar_url, user_id))
            conn.commit()

    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        profile_picture_url: Optional[str] = None,
        role: str = "Lead Risk Officer",
        organization: str = "FinSecure Inc.",
        clearance: str = "SuperAdmin • Level 4"
    ) -> Optional[Dict[str, Any]]:
        clean_email = email.strip().lower()
        avatar = profile_picture_url or get_email_avatar_url(clean_email)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash, profile_picture_url, role, organization, clearance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name.strip(),
                    clean_email,
                    password_hash,
                    avatar,
                    role,
                    organization,
                    clearance
                )
            )
            conn.commit()
            new_id = cursor.lastrowid
            if new_id is not None:
                return self.get_user_by_id(new_id)
            return None

    def update_user_password_by_email(self, email: str, password_hash: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE LOWER(email) = ?", (password_hash, email.strip().lower()))
            conn.commit()
            return cursor.rowcount > 0

    def create_password_reset(
        self,
        email: str,
        token: str,
        code: str,
        expires_at: float,
        ip_address: str = "127.0.0.1",
        user_agent: str = "Web Client"
    ) -> Dict[str, Any]:
        clean_email = email.strip().lower()
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Invalidate any older unused reset tokens for this email
            cursor.execute("UPDATE password_resets SET used_at = ? WHERE LOWER(email) = ? AND used_at IS NULL", (now, clean_email))
            cursor.execute(
                """
                INSERT INTO password_resets (email, token, code, created_at, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (clean_email, token, code, now, expires_at, ip_address, user_agent)
            )
            conn.commit()
            new_id = cursor.lastrowid
            return {
                "id": new_id,
                "email": clean_email,
                "token": token,
                "code": code,
                "created_at": now,
                "expires_at": expires_at,
                "ip_address": ip_address,
                "user_agent": user_agent
            }

    def get_password_reset(self, token_or_code: str, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        clean_val = token_or_code.strip()
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if email:
                clean_email = email.strip().lower()
                cursor.execute(
                    """
                    SELECT * FROM password_resets 
                    WHERE (token = ? OR code = ?) AND LOWER(email) = ? AND used_at IS NULL AND expires_at > ?
                    ORDER BY id DESC LIMIT 1
                    """,
                    (clean_val, clean_val, clean_email, now)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM password_resets 
                    WHERE (token = ? OR code = ?) AND used_at IS NULL AND expires_at > ?
                    ORDER BY id DESC LIMIT 1
                    """,
                    (clean_val, clean_val, now)
                )
            row = cursor.fetchone()
            return dict(row) if row else None

    def mark_password_reset_used(self, reset_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE password_resets SET used_at = ? WHERE id = ?", (time.time(), reset_id))
            conn.commit()
            return cursor.rowcount > 0

    # =========================================================================
    # SOC Audit & Event Logs (SQLite) - Level 4 Full Authority Tracking
    # =========================================================================
    def log_audit_event(
        self,
        action: str,
        actor: str = "Anonymous User",
        target: str = "SYSTEM",
        status: str = "SUCCESS",
        details: str = "",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        clearance: Optional[str] = None
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_logs (timestamp, action, actor, target, status, details, ip_address, user_agent, clearance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    time.time(),
                    action,
                    actor,
                    target,
                    status,
                    details,
                    ip_address or "127.0.0.1",
                    user_agent or "Web Browser",
                    clearance or "Level 4: SuperAdmin"
                )
            )
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid is not None else 0

    def get_recent_audit_logs(
        self,
        limit: int = 50,
        action_filter: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params: List[Any] = []

            if action_filter and action_filter.upper() != "ALL":
                query += " AND action LIKE ?"
                params.append(f"%{action_filter.strip().upper()}%")

            if search_term and search_term.strip():
                s = f"%{search_term.strip()}%"
                query += " AND (actor LIKE ? OR target LIKE ? OR details LIKE ? OR ip_address LIKE ?)"
                params.extend([s, s, s, s])

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, tuple(params))
            rows = [dict(r) for r in cursor.fetchall()]

            # Enrich with readable dates and relative time
            now = time.time()
            for r in rows:
                ts = r.get("timestamp") or now
                r["datetime_str"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts))
                diff = max(0, int(now - ts))
                if diff < 60:
                    r["time_ago"] = f"{diff}s ago"
                elif diff < 3600:
                    r["time_ago"] = f"{diff // 60}m ago"
                elif diff < 86400:
                    r["time_ago"] = f"{diff // 3600}h ago"
                else:
                    r["time_ago"] = f"{diff // 86400}d ago"
            return rows

    def get_audit_summary_stats(self) -> Dict[str, Any]:
        """Calculates security summary metrics for Level 4 Full Authority inspection."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'LOGIN_SUCCESS'")
            successful_logins = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'LOGIN_FAILED'")
            failed_logins = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'ACCOUNT_CREATED'")
            accounts_created = cursor.fetchone()[0]

            cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 1")
            last_event_row = cursor.fetchone()
            last_event = dict(last_event_row) if last_event_row else None

            return {
                "total_users": total_users,
                "successful_logins": successful_logins,
                "failed_logins": failed_logins,
                "accounts_created": accounts_created,
                "total_events": successful_logins + failed_logins + accounts_created,
                "last_event": last_event
            }

db = Database()
