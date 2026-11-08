import time
from collections import deque
from typing import Dict, Any, Deque
from backend.app.models.schemas.transaction import Transaction
from backend.app.utils.geo_calc import calculate_speed_kmh

class SlidingWindowBufferManager:
    def __init__(self, window_seconds: int = 300):
        self.window_seconds = window_seconds
        # User -> deque of (timestamp, amount, lat, lon)
        self.user_history: Dict[str, Deque] = {}
        # Card -> deque of (timestamp, amount)
        self.card_history: Dict[str, Deque] = {}
        # Device registry
        self.known_devices: set = set()

    def extract_features(self, tx: Transaction) -> Dict[str, Any]:
        now = tx.timestamp or time.time()
        user_id = tx.user_id or "ANON"
        
        if user_id not in self.user_history:
            self.user_history[user_id] = deque()
        u_queue = self.user_history[user_id]
        
        # Evict old events
        cutoff = now - self.window_seconds
        while u_queue and u_queue[0]["time"] < cutoff:
            u_queue.popleft()

        # Velocity in last 60s and 5m
        tx_count_60s = sum(1 for e in u_queue if e["time"] >= now - 60)
        tx_count_5m = len(u_queue)

        # Impossible Travel Speed
        geo_speed_kmh = 0.0
        if u_queue and tx.location and tx.location.lat is not None and tx.location.lon is not None:
            last = u_queue[-1]
            if last.get("lat") is not None and last.get("lon") is not None:
                geo_speed_kmh = calculate_speed_kmh(
                    last["lat"], last["lon"], last["time"],
                    tx.location.lat, tx.location.lon, now
                )

        # Micro probe detection (< $5 transactions followed by high volume)
        has_micro_probe_prior = any(e["amount"] < 5.0 for e in u_queue) and (tx.amount > 500.0)

        # New device detection
        is_new_device = tx.device_id not in self.known_devices if tx.device_id else False
        if tx.device_id:
            self.known_devices.add(tx.device_id)

        # Amount Z-score approximation
        amounts = [e["amount"] for e in u_queue]
        if amounts:
            avg_amt = sum(amounts) / len(amounts)
            variance = sum((x - avg_amt) ** 2 for x in amounts) / len(amounts)
            std_dev = (variance ** 0.5) if variance > 0 else 50.0
            amount_z_score = round(max(-3.0, min(10.0, (tx.amount - avg_amt) / max(std_dev, 1.0))), 2)
        else:
            amount_z_score = 0.0

        # Record this event
        lat = tx.location.lat if tx.location else None
        lon = tx.location.lon if tx.location else None
        u_queue.append({"time": now, "amount": tx.amount, "lat": lat, "lon": lon})

        return {
            "geo_speed_kmh": geo_speed_kmh,
            "tx_count_60s": tx_count_60s,
            "tx_count_5m": tx_count_5m,
            "has_micro_probe_prior": has_micro_probe_prior,
            "is_new_device": is_new_device,
            "amount_z_score": amount_z_score,
            "amount": tx.amount,
            "is_vpn_tor": tx.is_vpn_tor
        }

buffer_manager = SlidingWindowBufferManager()

