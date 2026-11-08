from collections import defaultdict
from typing import Dict, Any, List

class EntityGraphService:
    def __init__(self):
        # User -> devices, IPs, cards
        self.device_users: Dict[str, set] = defaultdict(set)
        self.ip_users: Dict[str, set] = defaultdict(set)
        self.card_users: Dict[str, set] = defaultdict(set)
        self.clusters: Dict[str, str] = {}
        self.cluster_counter = 100

    def add_transaction_link(self, user_id: str, card_id: str, device_id: str, ip_address: str) -> Dict[str, Any]:
        self.device_users[device_id].add(user_id)
        self.ip_users[ip_address].add(user_id)
        self.card_users[card_id].add(user_id)

        shared_dev = len(self.device_users[device_id])
        shared_ip = len(self.ip_users[ip_address])
        shared_card = len(self.card_users[card_id])

        graph_risk_score = 0.0
        explanations = []
        cluster_id = None

        if shared_dev >= 3:
            cluster_id = f"MULE_RING_{device_id[:6].upper()}"
            graph_risk_score += 45.0
            explanations.append(f"Device {device_id} is linked to {shared_dev} distinct customer identities (Mule Syndicate signature)")

        if shared_ip >= 4:
            graph_risk_score += 30.0
            explanations.append(f"IP {ip_address} has routed transactions across {shared_ip} user accounts")

        if shared_card >= 2:
            graph_risk_score += 40.0
            explanations.append(f"Payment card {card_id} is actively associated with {shared_card} accounts (Card Sharing/Harvesting)")

        return {
            "graph_risk_score": round(min(100.0, graph_risk_score), 1),
            "shared_users_on_device": shared_dev,
            "shared_users_on_ip": shared_ip,
            "cluster_id": cluster_id,
            "explanations": explanations
        }

    def get_network_topology(self) -> Dict[str, Any]:
        nodes = []
        edges = []
        # Return sample nodes and edges for network graph visualization
        for dev, users in list(self.device_users.items())[:15]:
            nodes.append({"id": dev, "label": f"DEV: {dev[:8]}", "type": "device", "risk": "CRITICAL" if len(users) >= 3 else "LOW"})
            for u in list(users)[:5]:
                nodes.append({"id": u, "label": u, "type": "user", "risk": "MEDIUM"})
                edges.append({"from": u, "to": dev, "relationship": "USES_DEVICE"})
        return {"nodes": nodes, "edges": edges}

graph_service = EntityGraphService()

