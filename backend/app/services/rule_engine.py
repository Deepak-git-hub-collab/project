import logging
from typing import Dict, List, Tuple, Any
from backend.app.core.database import db
from backend.app.models.schemas.rule import DetectionRule
from backend.app.models.schemas.transaction import Transaction, RiskFactor

logger = logging.getLogger("shieldplus.rules")

class RuleEvaluationEngine:
    def __init__(self):
        self.cached_rules: List[DetectionRule] = []
        self.reload_rules()

    def reload_rules(self):
        try:
            self.cached_rules = db.get_all_rules()
        except Exception:
            self.cached_rules = []

    def evaluate(self, tx: Transaction, features: Dict[str, Any], graph_context: Dict[str, Any]) -> Tuple[float, List[str], List[RiskFactor], str]:
        """
        Evaluates active rules against transaction, engineered features, and graph links.
        Returns: (rule_score, triggered_rule_ids, factors, forced_action)
        """
        rule_score = 0.0
        triggered_rules = []
        factors = []
        forced_action = "APPROVE"  # or "FLAG", "BLOCK"

        eval_context = {
            "amount": tx.amount,
            "currency": tx.currency,
            "merchant": tx.merchant,
            "merchant_category": tx.merchant_category,
            "channel": tx.channel,
            "is_vpn_tor": tx.is_vpn_tor,
            "geo_speed_kmh": features.get("geo_speed_kmh", 0.0),
            "tx_count_60s": features.get("tx_count_60s", 0),
            "tx_count_5m": features.get("tx_count_5m", 0),
            "has_micro_probe_prior": features.get("has_micro_probe_prior", False),
            "is_new_device": features.get("is_new_device", False),
            "amount_z_score": features.get("amount_z_score", 0.0),
            "graph_shared_entities": graph_context.get("shared_users_on_device", 1)
        }

        for rule in self.cached_rules:
            if not rule.enabled:
                continue

            matched = False
            try:
                matched = bool(eval(rule.condition_code, {"__builtins__": None}, eval_context))
            except Exception:
                matched = self._fallback_match(rule, eval_context)

            if matched:
                triggered_rules.append(rule.name)
                rule_score += rule.weight
                
                severity = "CRITICAL" if rule.action == "BLOCK" else "WARNING"
                factors.append(RiskFactor(
                    factor_name=f"Rule: {rule.name}",
                    contribution=rule.weight,
                    description=rule.description,
                    severity=severity
                ))

                if rule.action == "BLOCK":
                    forced_action = "BLOCK"
                elif rule.action == "FLAG" and forced_action != "BLOCK":
                    forced_action = "FLAG"

        return rule_score, triggered_rules, factors, forced_action

    def _fallback_match(self, rule: DetectionRule, ctx: Dict[str, Any]) -> bool:
        cond = (rule.condition_code or "").lower()
        if "geo_speed_kmh" in cond and ctx.get("geo_speed_kmh", 0) > 800:
            return True
        if "tx_count_60s" in cond and ctx.get("tx_count_60s", 0) >= 4:
            return True
        if "is_vpn_tor" in cond and ctx.get("is_vpn_tor", False):
            return True
        if "amount" in cond and ctx.get("amount", 0) > 10000:
            return True
        return False

rule_engine = RuleEvaluationEngine()
