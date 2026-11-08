import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import db

client = TestClient(app)

class TestGeoCityMetrics(unittest.TestCase):
    def test_distinct_cities_and_countries(self):
        # Test countries endpoint
        res = client.get("/api/v1/transactions/countries")
        self.assertEqual(res.status_code, 200)
        countries = res.json()
        self.assertIn("India", countries)
        self.assertIn("United States", countries)
        self.assertIn("Japan", countries)

        # Test cities endpoint
        res = client.get("/api/v1/transactions/cities?country=India")
        self.assertEqual(res.status_code, 200)
        cities = res.json()
        self.assertIn("Mumbai", cities)
        self.assertIn("Bengaluru", cities)
        self.assertIn("Delhi", cities)

    def test_city_metrics_authentic_rates(self):
        # Global metrics: should be authentic rate from real database
        res = client.get("/api/v1/metrics")
        self.assertEqual(res.status_code, 200)
        m_global = res.json()
        self.assertGreater(m_global["total_transactions"], 100000)
        self.assertLess(m_global["fraud_rate_pct"], 50.0)
        self.assertGreater(m_global["donut"]["low"], 50.0)

        # India metrics: authentic rate from SQLite database
        res = client.get("/api/v1/metrics?country=India")
        self.assertEqual(res.status_code, 200)
        m_india = res.json()
        self.assertGreater(m_india["total_transactions"], 15000)
        self.assertLess(m_india["fraud_rate_pct"], 50.0)
        self.assertGreaterEqual(m_india["donut"]["low"], 50.0)

        # Mumbai city metrics
        res = client.get("/api/v1/metrics?country=India&state=Mumbai")
        self.assertEqual(res.status_code, 200)
        m_mumbai = res.json()
        self.assertGreater(m_mumbai["total_transactions"], 3000)
        self.assertLess(m_mumbai["fraud_rate_pct"], 45.0)
        self.assertGreater(m_mumbai["donut"]["low"], 55.0)

        # Mumbai with city param
        res = client.get("/api/v1/metrics?country=India&city=Mumbai")
        self.assertEqual(res.status_code, 200)
        m_mumbai_city = res.json()
        self.assertEqual(m_mumbai["total_transactions"], m_mumbai_city["total_transactions"])

    def test_city_transactions_query(self):
        # Query transactions filtered by city
        res = client.get("/api/v1/transactions?country=India&city=Mumbai&limit=10")
        self.assertEqual(res.status_code, 200)
        txs = res.json()
        self.assertGreater(len(txs), 0)
        for t in txs:
            loc = t["transaction"]["location"]
            self.assertEqual(loc["city"], "Mumbai")
            self.assertEqual(loc["country"], "India")

    def test_activity_timeseries_endpoint(self):
        # 1. Global Daily activity
        res = client.get("/api/v1/metrics/activity?timeframe=Daily")
        self.assertEqual(res.status_code, 200)
        act_global = res.json()
        self.assertEqual(len(act_global["labels"]), 7)
        self.assertEqual(len(act_global["legitimate"]), 7)
        self.assertEqual(len(act_global["fraudulent"]), 7)
        self.assertGreater(act_global["total_transactions"], 1000)

        # 2. India Daily activity
        res = client.get("/api/v1/metrics/activity?country=India&timeframe=Daily")
        self.assertEqual(res.status_code, 200)
        act_india = res.json()
        self.assertGreater(act_india["total_transactions"], 100)
        self.assertLess(act_india["total_transactions"], act_global["total_transactions"])

        # 3. Mumbai City Daily activity
        res = client.get("/api/v1/metrics/activity?country=India&city=Mumbai&timeframe=Daily")
        self.assertEqual(res.status_code, 200)
        act_mumbai = res.json()
        self.assertGreater(act_mumbai["total_transactions"], 20)
        self.assertLess(act_mumbai["total_transactions"], act_india["total_transactions"])
        self.assertGreater(act_mumbai["legit_total"], 0)
        self.assertGreater(act_mumbai["fraud_total"], 0)

        # 4. Weekly and Monthly timeframes
        res_wk = client.get("/api/v1/metrics/activity?country=India&city=Mumbai&timeframe=Weekly")
        self.assertEqual(res_wk.status_code, 200)
        self.assertEqual(len(res_wk.json()["labels"]), 7)

        res_mo = client.get("/api/v1/metrics/activity?country=India&city=Mumbai&timeframe=Monthly")
        self.assertEqual(res_mo.status_code, 200)
        self.assertEqual(len(res_mo.json()["labels"]), 5)

    def test_metrics_timeframe_filtering(self):
        # 1. Test 30 vs 7 vs 24 hours on global metrics
        res_30 = client.get("/api/v1/metrics?timeframe=30")
        self.assertEqual(res_30.status_code, 200)
        m_30 = res_30.json()

        res_24 = client.get("/api/v1/metrics?timeframe=24")
        self.assertEqual(res_24.status_code, 200)
        m_24 = res_24.json()

        self.assertGreaterEqual(m_30["total_transactions"], m_24["total_transactions"])
        self.assertIn("donut", m_24)
        self.assertGreater(m_24["donut"]["low"], 0.0)

        # 2. Test India with timeframe
        res_in_24 = client.get("/api/v1/metrics?country=India&timeframe=24")
        self.assertEqual(res_in_24.status_code, 200)
        m_in_24 = res_in_24.json()
        self.assertGreater(m_in_24["total_transactions"], 500)
        self.assertGreater(m_in_24["fraud_rate_pct"], 0.0)
        self.assertLessEqual(m_in_24["fraud_rate_pct"], 100.0)

if __name__ == "__main__":
    unittest.main()

