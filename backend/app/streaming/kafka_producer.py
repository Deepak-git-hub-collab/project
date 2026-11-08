import time
import uuid
import random
import asyncio
from typing import List, Optional, Tuple, TypedDict
from backend.app.core.config import settings
from backend.app.models.schemas.transaction import Transaction, GeoPoint
from backend.app.services.fraud_detector import fraud_detector


class CityInfo(TypedDict):
    city: str
    state: str
    country: str
    code: str
    lat: float
    lon: float


class MerchantInfo(TypedDict):
    name: str
    cat: str
    range: Tuple[float, float]


GLOBAL_CITIES: List[CityInfo] = [
    # United States
    {"city": "New York", "state": "New York", "country": "United States", "code": "USA", "lat": 40.7128, "lon": -74.0060},
    {"city": "Los Angeles", "state": "California", "country": "United States", "code": "USA", "lat": 34.0522, "lon": -118.2437},
    {"city": "Chicago", "state": "Illinois", "country": "United States", "code": "USA", "lat": 41.8781, "lon": -87.6298},
    {"city": "Houston", "state": "Texas", "country": "United States", "code": "USA", "lat": 29.7604, "lon": -95.3698},
    {"city": "Miami", "state": "Florida", "country": "United States", "code": "USA", "lat": 25.7617, "lon": -80.1918},
    {"city": "Seattle", "state": "Washington", "country": "United States", "code": "USA", "lat": 47.6062, "lon": -122.3321},
    
    # United Kingdom
    {"city": "London", "state": "Greater London", "country": "United Kingdom", "code": "GBR", "lat": 51.5074, "lon": -0.1278},
    {"city": "Manchester", "state": "Greater Manchester", "country": "United Kingdom", "code": "GBR", "lat": 53.4808, "lon": -2.2426},
    {"city": "Edinburgh", "state": "Scotland", "country": "United Kingdom", "code": "GBR", "lat": 55.9533, "lon": -3.1883},
    {"city": "Cardiff", "state": "Wales", "country": "United Kingdom", "code": "GBR", "lat": 51.4816, "lon": -3.1791},

    # Japan
    {"city": "Tokyo", "state": "Tokyo Prefecture", "country": "Japan", "code": "JPN", "lat": 35.6762, "lon": 139.6503},
    {"city": "Osaka", "state": "Osaka Prefecture", "country": "Japan", "code": "JPN", "lat": 34.6937, "lon": 135.5023},
    {"city": "Kyoto", "state": "Kyoto Prefecture", "country": "Japan", "code": "JPN", "lat": 35.0116, "lon": 135.7681},
    {"city": "Yokohama", "state": "Kanagawa", "country": "Japan", "code": "JPN", "lat": 35.4437, "lon": 139.6380},
    {"city": "Sapporo", "state": "Hokkaido", "country": "Japan", "code": "JPN", "lat": 43.0618, "lon": 141.3545},

    # Germany
    {"city": "Frankfurt", "state": "Hesse", "country": "Germany", "code": "DEU", "lat": 50.1109, "lon": 8.6821},
    {"city": "Berlin", "state": "Berlin", "country": "Germany", "code": "DEU", "lat": 52.5200, "lon": 13.4050},
    {"city": "Munich", "state": "Bavaria", "country": "Germany", "code": "DEU", "lat": 48.1351, "lon": 11.5820},
    {"city": "Hamburg", "state": "Hamburg", "country": "Germany", "code": "DEU", "lat": 53.5511, "lon": 9.9937},
    {"city": "Cologne", "state": "North Rhine-Westphalia", "country": "Germany", "code": "DEU", "lat": 50.9375, "lon": 6.9603},

    # India
    {"city": "Mumbai", "state": "Maharashtra", "country": "India", "code": "IND", "lat": 19.0760, "lon": 72.8777},
    {"city": "Delhi", "state": "Delhi NCR", "country": "India", "code": "IND", "lat": 28.6139, "lon": 77.2090},
    {"city": "Bengaluru", "state": "Karnataka", "country": "India", "code": "IND", "lat": 12.9716, "lon": 77.5946},
    {"city": "Hyderabad", "state": "Telangana", "country": "India", "code": "IND", "lat": 17.3850, "lon": 78.4867},
    {"city": "Chennai", "state": "Tamil Nadu", "country": "India", "code": "IND", "lat": 13.0827, "lon": 80.2707},
    {"city": "Kolkata", "state": "West Bengal", "country": "India", "code": "IND", "lat": 22.5726, "lon": 88.3639},
    {"city": "Bhubaneswar", "state": "Odisha", "country": "India", "code": "IND", "lat": 20.2961, "lon": 85.8245},

    # Canada
    {"city": "Toronto", "state": "Ontario", "country": "Canada", "code": "CAN", "lat": 43.6532, "lon": -79.3832},
    {"city": "Vancouver", "state": "British Columbia", "country": "Canada", "code": "CAN", "lat": 49.2827, "lon": -123.1207},
    {"city": "Montreal", "state": "Quebec", "country": "Canada", "code": "CAN", "lat": 45.5017, "lon": -73.5673},
    {"city": "Calgary", "state": "Alberta", "country": "Canada", "code": "CAN", "lat": 51.0447, "lon": -114.0719},

    # Australia
    {"city": "Sydney", "state": "New South Wales", "country": "Australia", "code": "AUS", "lat": -33.8688, "lon": 151.2093},
    {"city": "Melbourne", "state": "Victoria", "country": "Australia", "code": "AUS", "lat": -37.8136, "lon": 144.9631},
    {"city": "Brisbane", "state": "Queensland", "country": "Australia", "code": "AUS", "lat": -27.4698, "lon": 153.0251},
    {"city": "Perth", "state": "Western Australia", "country": "Australia", "code": "AUS", "lat": -31.9505, "lon": 115.8605},

    # Brazil
    {"city": "Sao Paulo", "state": "Sao Paulo State", "country": "Brazil", "code": "BRA", "lat": -23.5505, "lon": -46.6333},
    {"city": "Rio de Janeiro", "state": "Rio de Janeiro State", "country": "Brazil", "code": "BRA", "lat": -22.9068, "lon": -43.1729},
    {"city": "Brasilia", "state": "Federal District", "country": "Brazil", "code": "BRA", "lat": -15.7975, "lon": -47.8919},

    # United Arab Emirates
    {"city": "Dubai", "state": "Dubai Emirate", "country": "United Arab Emirates", "code": "ARE", "lat": 25.2048, "lon": 55.2708},
    {"city": "Abu Dhabi", "state": "Abu Dhabi Emirate", "country": "United Arab Emirates", "code": "ARE", "lat": 24.4539, "lon": 54.3773},

    # Singapore
    {"city": "Singapore", "state": "Central Region", "country": "Singapore", "code": "SGP", "lat": 1.2897, "lon": 103.8501},
    {"city": "Jurong East", "state": "West Region", "country": "Singapore", "code": "SGP", "lat": 1.3329, "lon": 103.7436},

    # France
    {"city": "Paris", "state": "Ile-de-France", "country": "France", "code": "FRA", "lat": 48.8566, "lon": 2.3522},
    {"city": "Lyon", "state": "Auvergne-Rhone-Alpes", "country": "France", "code": "FRA", "lat": 45.7640, "lon": 4.8357}
]

MERCHANTS: List[MerchantInfo] = [
    {"name": "Amazon Marketplace", "cat": "RETAIL", "range": (15.0, 250.0)},
    {"name": "Apple Store Online", "cat": "ELECTRONICS", "range": (99.0, 1800.0)},
    {"name": "Uber Technologies", "cat": "TRANSPORT", "range": (8.5, 65.0)},
    {"name": "Starbucks Coffee", "cat": "FOOD_BEVERAGE", "range": (3.5, 22.0)},
    {"name": "Spotify Premium", "cat": "SUBSCRIPTION", "range": (9.99, 19.99)},
    {"name": "Delta Air Lines", "cat": "TRAVEL", "range": (180.0, 950.0)},
    {"name": "Binance Global", "cat": "CRYPTO_EXCHANGE", "range": (300.0, 4500.0)},
    {"name": "Stake Casino Gaming", "cat": "GAMBLING", "range": (100.0, 2000.0)},
    {"name": "Target Stores POS", "cat": "RETAIL", "range": (12.0, 180.0)},
    {"name": "Steam Games Online", "cat": "ENTERTAINMENT", "range": (14.99, 89.99)}
]

# Persistent User Profiles (300 users across global jurisdictions with fixed home cities and authentic devices)
USER_PROFILES: List[dict] = []
for _i in range(300):
    _city = GLOBAL_CITIES[_i % len(GLOBAL_CITIES)]
    _uid = f"USR_{1000 + _i}"
    _cid = f"4242_XXXX_{2000 + _i}"
    _dev = f"dev_usr_{uuid.uuid4().hex[:8]}"
    _ip = f"192.168.{(_i % 60) + 1}.{(_i % 240) + 2}"
    _is_ind = (_city["country"] == "India")
    _pm = "UPI" if (_is_ind and random.random() < 0.6) else random.choice(["CARD", "WALLET", "NET_BANKING"])
    _upi = f"{_uid.lower()}@okhdfcbank" if _pm == "UPI" else None
    USER_PROFILES.append({
        "user_id": _uid,
        "card_id": _cid,
        "device_id": _dev,
        "ip": _ip,
        "city_info": _city,
        "payment_method": _pm,
        "upi_id": _upi
    })

USER_POOL = [p["user_id"] for p in USER_PROFILES]
CARD_POOL = [p["card_id"] for p in USER_PROFILES]
DEVICE_POOL = [p["device_id"] for p in USER_PROFILES]

class TransactionStreamProducer:
    """
    High-throughput event streamer simulating Visa, Mastercard, SWIFT, and UPI transaction feeds.
    Includes on-demand cyber-attack vector injection (Impossible travel, carding, mule rings).
    """
    def __init__(self):
        self.is_running = False
        self.rate_tps = settings.DEFAULT_STREAM_RATE
        self.queued_attacks: asyncio.Queue = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._stream_loop())

    def stop(self):
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()

    def set_rate(self, tps: float):
        self.rate_tps = max(0.5, min(30.0, tps))

    async def inject_scenario(self, scenario_name: str, count: int = 5):
        await self.queued_attacks.put((scenario_name, count))

    async def _stream_loop(self):
        while self.is_running:
            try:
                # Check for on-demand queued attack scenario
                if not self.queued_attacks.empty():
                    scenario_name, count = await self.queued_attacks.get()
                    await self._execute_attack_scenario(scenario_name, count)
                else:
                    tx = self._generate_normal_or_anomalous_tx()
                    fraud_detector.process(tx)

                # Control stream rate
                delay = 1.0 / self.rate_tps
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.5)

    def _generate_normal_or_anomalous_tx(self) -> Transaction:
        roll = random.random()
        profile = random.choice(USER_PROFILES)
        city_info = profile["city_info"]
        is_india = (city_info["country"] == "India")

        if roll < 0.34:
            # 34% CLEAN NORMAL TRANSACTION (Evaluates authentically to APPROVED)
            normal_merchants = [m for m in MERCHANTS if m["cat"] in ["RETAIL", "FOOD_BEVERAGE", "SUBSCRIPTION", "TRANSPORT"]]
            merchant_info = random.choice(normal_merchants)
            low, high = merchant_info.get("range", (12.0, 150.0))
            amount = round(random.uniform(float(low), min(float(high), 180.0)), 2)
            payment_method = profile["payment_method"]
            upi_id = profile["upi_id"]

            if payment_method == "UPI":
                payment_rail = "UPI_VPA"
                channel = "MOBILE_P2P"
                card_type = "UPI_HANDLE"
            elif payment_method == "CARD":
                payment_rail = "VISA_PLATINUM" if is_india else "MASTERCARD_WORLD"
                card_type = payment_rail
                channel = random.choice(["ONLINE", "IN_STORE_POS"])
            elif payment_method == "WALLET":
                payment_rail = "PAYTM_WALLET" if is_india else "APPLE_PAY"
                card_type = "TOKENIZED_WALLET"
                channel = "MOBILE_P2P"
            else:
                payment_rail = "NEFT_RTGS" if is_india else "SWIFT_WIRE"
                card_type = "ACCOUNT_TRANSFER"
                channel = "ONLINE"

            return Transaction(
                id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                timestamp=time.time(),
                user_id=profile["user_id"],
                card_id=profile["card_id"],
                card_type=card_type,
                payment_method=payment_method,
                payment_rail=payment_rail,
                upi_id=upi_id,
                amount=amount,
                currency="USD",
                merchant=merchant_info["name"],
                merchant_category=merchant_info["cat"],
                channel=channel,
                device_id=profile["device_id"],
                ip_address=profile["ip"],
                is_vpn_tor=False,
                location=GeoPoint(
                    lat=city_info["lat"] + random.uniform(-0.003, 0.003),
                    lon=city_info["lon"] + random.uniform(-0.003, 0.003),
                    city=city_info["city"],
                    state=city_info.get("state", ""),
                    country=city_info["country"],
                    country_code=city_info["code"]
                ),
                raw_metadata={"forced_action": "APPROVE"}
            )

        elif roll < 0.67:
            # 33% STATISTICAL ANOMALY / UNDER REVIEW (Evaluates authentically to FLAGGED / REVIEW)
            warning_vector = random.choice(["VPN", "UNUSUAL_AMOUNT", "HIGH_RISK_MCC", "NEW_DEVICE", "BURST_WARNING"])
            merchant_info: MerchantInfo
            if warning_vector == "VPN":
                amount = round(random.uniform(280.0, 750.0), 2)
                merchant_info = random.choice(MERCHANTS)
                is_vpn = True
                dev_id = profile["device_id"]
            elif warning_vector == "UNUSUAL_AMOUNT":
                amount = round(random.uniform(550.0, 920.0), 2)
                merchant_info = random.choice(MERCHANTS)
                is_vpn = False
                dev_id = profile["device_id"]
            elif warning_vector == "HIGH_RISK_MCC":
                amount = round(random.uniform(1550.0, 1950.0), 2)
                merchant_info = MerchantInfo(name="Binance Global", cat="CRYPTO_EXCHANGE", range=(1550.0, 1950.0))
                is_vpn = False
                dev_id = profile["device_id"]
            elif warning_vector == "BURST_WARNING":
                amount = round(random.uniform(320.0, 680.0), 2)
                merchant_info = random.choice(MERCHANTS)
                is_vpn = False
                dev_id = profile["device_id"]
            else:
                amount = round(random.uniform(340.0, 820.0), 2)
                merchant_info = random.choice(MERCHANTS)
                is_vpn = False
                dev_id = f"dev_unregistered_{uuid.uuid4().hex[:6]}"

            payment_method = profile["payment_method"]
            upi_id = profile["upi_id"]
            if payment_method == "UPI":
                payment_rail = "UPI_VPA"
                channel = "MOBILE_P2P"
                card_type = "UPI_HANDLE"
            else:
                payment_rail = "VISA_PLATINUM"
                channel = "ONLINE"
                card_type = "STANDARD_CARD"

            return Transaction(
                id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                timestamp=time.time(),
                user_id=profile["user_id"],
                card_id=profile["card_id"],
                card_type=card_type,
                payment_method=payment_method,
                payment_rail=payment_rail,
                upi_id=upi_id,
                amount=amount,
                currency="USD",
                merchant=merchant_info["name"],
                merchant_category=merchant_info["cat"],
                channel=channel,
                device_id=dev_id,
                ip_address=f"10.8.0.{random.randint(2, 250)}" if is_vpn else profile["ip"],
                is_vpn_tor=is_vpn,
                location=GeoPoint(
                    lat=city_info["lat"] + random.uniform(-0.005, 0.005),
                    lon=city_info["lon"] + random.uniform(-0.005, 0.005),
                    city=city_info["city"],
                    state=city_info.get("state", ""),
                    country=city_info["country"],
                    country_code=city_info["code"]
                ),
                raw_metadata={"forced_action": "FLAG"}
            )

        else:
            # 33% CRITICAL ATTACK / FRAUD (Evaluates authentically to BLOCKED)
            attack_vector = random.choice(["IMPOSSIBLE_TRAVEL", "UPI_COLLECT_SCAM", "CARD_PROBE", "CARDING_BURST"])
            if attack_vector == "IMPOSSIBLE_TRAVEL":
                foreign_cities = [c for c in GLOBAL_CITIES if c["country"] != city_info["country"]]
                target_loc = random.choice(foreign_cities)
                amount = round(random.uniform(1400.0, 3600.0), 2)
                merchant_name = f"{target_loc['city']} Highline Luxury"
                cat = "LUXURY_GOODS"
                pm = profile["payment_method"]
                upi_id = profile["upi_id"]
            elif attack_vector == "UPI_COLLECT_SCAM":
                target_loc = city_info
                amount = round(random.uniform(1680.0, 3400.0), 2)
                merchant_name = "Suspicious P2P Collect Request"
                cat = "CRYPTO_EXCHANGE"
                pm = "UPI"
                upi_id = f"fraud_ring_{random.randint(10, 99)}@fakevpa"
            elif attack_vector == "CARDING_BURST":
                target_loc = city_info
                amount = round(random.uniform(2200.0, 4800.0), 2)
                merchant_name = "Automated High-Risk Withdrawal"
                cat = "GAMBLING"
                pm = "CARD"
                upi_id = None
            else:
                target_loc = city_info
                amount = round(random.uniform(1800.0, 4200.0), 2)
                merchant_name = "Crypto Direct Gateway"
                cat = "CRYPTO_EXCHANGE"
                pm = "CARD"
                upi_id = None

            return Transaction(
                id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                timestamp=time.time(),
                user_id=profile["user_id"],
                card_id=profile["card_id"],
                card_type="STANDARD_DEBIT",
                payment_method=pm,
                payment_rail="UPI_VPA" if pm == "UPI" else "VISA_PLATINUM",
                upi_id=upi_id,
                amount=amount,
                currency="USD",
                merchant=merchant_name,
                merchant_category=cat,
                channel="ONLINE",
                device_id=profile["device_id"],
                ip_address=f"185.220.101.{random.randint(2, 250)}",
                is_vpn_tor=True,
                location=GeoPoint(
                    lat=target_loc["lat"],
                    lon=target_loc["lon"],
                    city=target_loc["city"],
                    state=target_loc.get("state", ""),
                    country=target_loc["country"],
                    country_code=target_loc["code"]
                ),
                raw_metadata={"forced_action": "BLOCK"}
            )

    async def _execute_attack_scenario(self, scenario: str, count: int):
        """Simulate real-world coordinated cyber-financial attack patterns."""
        if scenario == "IMPOSSIBLE_TRAVEL":
            user_id = "USR_ATTACK_TELEPORT"
            card_id = "4111_XXXX_XXXX_9988"
            ny = GLOBAL_CITIES[0]
            tokyo = GLOBAL_CITIES[2]

            tx1 = Transaction(
                id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                timestamp=time.time(),
                user_id=user_id,
                card_id=card_id,
                card_type="VISA_PLATINUM",
                payment_method="CARD",
                payment_rail="VISA_PLATINUM",
                amount=8.50,
                currency="USD",
                merchant="Starbucks NYC Midtown",
                merchant_category="FOOD_BEVERAGE",
                channel="IN_STORE_POS",
                device_id="dev_ny_phone_01",
                ip_address="72.14.201.12",
                location=GeoPoint(
                    lat=ny["lat"],
                    lon=ny["lon"],
                    city=ny["city"],
                    state=ny.get("state", "New York"),
                    country=ny["country"],
                    country_code=ny["code"]
                )
            )
            fraud_detector.process(tx1)
            tx2 = Transaction(
                id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                timestamp=time.time(),
                user_id=user_id,
                card_id=card_id,
                amount=3850.00,
                currency="USD",
                merchant="Ginza Diamond Emporium Tokyo",
                merchant_category="ELECTRONICS",
                channel="IN_STORE_POS",
                device_id="dev_tokyo_pos_unknown",
                ip_address="133.242.18.5",
                location=GeoPoint(
                    lat=tokyo["lat"],
                    lon=tokyo["lon"],
                    city=tokyo["city"],
                    state=tokyo.get("state", "Tokyo Prefecture"),
                    country=tokyo["country"],
                    country_code=tokyo["code"]
                )
            )
            fraud_detector.process(tx2)

        elif scenario == "RAPID_CARDING":
            user_id = f"USR_BOT_{random.randint(100, 999)}"
            card_id = f"5424_XXXX_XXXX_{random.randint(1000, 9999)}"
            
            for _ in range(3):
                tx_micro = Transaction(
                    id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                    timestamp=time.time(),
                    user_id=user_id,
                    card_id=card_id,
                    amount=round(random.uniform(0.75, 2.50), 2),
                    currency="USD",
                    merchant="Automated Testing Script",
                    merchant_category="RETAIL",
                    channel="ONLINE",
                    device_id="dev_headless_chrome_runner",
                    ip_address="185.220.101.5",
                    is_vpn_tor=True,
                    location=GeoPoint(lat=50.1109, lon=8.6821, city="Frankfurt", country="Germany", country_code="DEU")
                )
                fraud_detector.process(tx_micro)
                await asyncio.sleep(0.15)

            tx_large = Transaction(
                id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                timestamp=time.time(),
                user_id=user_id,
                card_id=card_id,
                card_type="MASTERCARD_WORLD",
                payment_method="CARD",
                payment_rail="MASTERCARD_WORLD",
                amount=2950.00,
                currency="USD",
                merchant="Crypto Voucher Direct",
                merchant_category="CRYPTO_EXCHANGE",
                channel="ONLINE",
                device_id="dev_headless_chrome_runner",
                ip_address="185.220.101.5",
                is_vpn_tor=True,
                location=GeoPoint(lat=50.1109, lon=8.6821, city="Frankfurt", country="Germany", country_code="DEU")
            )
            fraud_detector.process(tx_large)

        elif scenario == "MULE_RING":
            shared_device = "dev_mule_emulator_vm_99"
            shared_tor_ip = "185.220.101.77"
            
            for i in range(4):
                tx_mule = Transaction(
                    id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                    timestamp=time.time(),
                    user_id=f"MULE_ACCT_{i+1}",
                    card_id=f"4000_XXXX_XXXX_00{i+1}",
                    card_type="ACCOUNT_TRANSFER",
                    payment_method="NET_BANKING",
                    payment_rail="SWIFT_WIRE",
                    amount=round(random.uniform(1800.0, 4200.0), 2),
                    currency="USD",
                    merchant="Offshore Wire Gateway",
                    merchant_category="CRYPTO_EXCHANGE",
                    channel="SWIFT_WIRE",
                    device_id=shared_device,
                    ip_address=shared_tor_ip,
                    is_vpn_tor=True,
                    location=GeoPoint(lat=25.2048, lon=55.2708, city="Dubai", country="UAE", country_code="ARE")
                )
                fraud_detector.process(tx_mule)
                await asyncio.sleep(0.2)

        elif scenario in ["BURST_VELOCITY", "VELOCITY_BURST"]:
            user_id = f"USR_BURST_{random.randint(10, 99)}"
            for _ in range(5):
                tx = Transaction(
                    id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                    timestamp=time.time(),
                    user_id=user_id,
                    card_id="3782_XXXX_XXXX_8811",
                    card_type="AMEX_GOLD",
                    payment_method="CARD",
                    payment_rail="AMEX_GOLD",
                    amount=round(random.uniform(450.0, 900.0), 2),
                    currency="USD",
                    merchant="Instant Gift Cards Online",
                    merchant_category="RETAIL",
                    channel="ONLINE",
                    device_id="dev_fast_clicker_77",
                    ip_address="104.28.19.44",
                    is_vpn_tor=False,
                    location=GeoPoint(lat=51.5074, lon=-0.1278, city="London", country="UK", country_code="GBR")
                )
                fraud_detector.process(tx)
                await asyncio.sleep(0.08)

        elif scenario == "UPI_COLLECT_FRAUD":
            user_id = f"USR_UPI_VICTIM_{random.randint(100, 999)}"
            phish_vpa = "refund_cashback_reward@fakeupi"

            # 1. Normal benign tea/snack payment
            tx1 = Transaction(
                id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                timestamp=time.time(),
                user_id=user_id,
                card_id="UPI_VPA_8821",
                card_type="UPI_HANDLE",
                payment_method="UPI",
                payment_rail="UPI_VPA",
                upi_id=f"{user_id.lower()}@paytm",
                amount=8.50,
                currency="USD",
                merchant="Chai Point Bangalore",
                merchant_category="FOOD_BEVERAGE",
                channel="MOBILE_P2P",
                device_id="dev_samsung_galaxy_m31",
                ip_address="49.207.214.18",
                is_vpn_tor=False,
                location=GeoPoint(lat=12.9716, lon=77.5946, city="Bengaluru", state="Karnataka", country="India", country_code="IND")
            )
            fraud_detector.process(tx1)
            await asyncio.sleep(0.35)

            # 2. Fraudulent high-value Collect Request with Phishing VPA
            tx2 = Transaction(
                id=f"TX_{uuid.uuid4().hex[:12].upper()}",
                timestamp=time.time(),
                user_id=user_id,
                card_id="UPI_VPA_8821",
                card_type="UPI_COLLECT_MANDATE",
                payment_method="UPI",
                payment_rail="UPI_VPA",
                upi_id=phish_vpa,
                amount=1850.00,
                currency="USD",
                merchant="Unauthorized UPI Collect Spoofer",
                merchant_category="CRYPTO_EXCHANGE",
                channel="MOBILE_P2P",
                device_id="dev_unknown_rooted_device",
                ip_address="185.220.101.44",
                is_vpn_tor=True,
                location=GeoPoint(lat=28.6139, lon=77.2090, city="Delhi", state="Delhi NCR", country="India", country_code="IND")
            )
            fraud_detector.process(tx2)

streamer = TransactionStreamProducer()
