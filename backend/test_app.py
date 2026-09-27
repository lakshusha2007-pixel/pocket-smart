import unittest
from starlette.testclient import TestClient
from main import app, get_db_connection
import database
import gemini_utils
import auth_utils

class TestPocketSmartApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        cls.client = TestClient(app)

    def test_00_landing_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("PocketSmart", response.text)
        self.assertIn("Smart Budget Simulator", response.text)
        self.assertIn("Three Purpose-Built Smart Planners", response.text)
        self.assertIn("Loved by Smart Budgeters Everywhere", response.text)
        self.assertIn("IKEA", response.text)
        self.assertIn("Swiggy", response.text)

    def test_01_login_page_renders(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome back", response.text)
        self.assertIn("PocketSmart", response.text)

    def test_02_login_and_dashboard_flow(self):
        response = self.client.post(
            "/login",
            data={"email": "demo@pocketsmart.ai", "password": "demo1234"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Dashboard", response.text)
        self.assertIn("Alex Johnson", response.text)
        self.assertIn("Home Interior", response.text)
        self.assertIn("Party Planner", response.text)
        self.assertIn("Jewelry Planner", response.text)

    def test_03_home_planner_flow(self):
        self.client.post("/login", data={"email": "demo@pocketsmart.ai", "password": "demo1234"})
        
        get_res = self.client.get("/planner/home")
        self.assertEqual(get_res.status_code, 200)
        self.assertIn("Home Interior Planner", get_res.text)

        post_res = self.client.post(
            "/planner/home",
            data={
                "budget": 60000,
                "room_type": "Living Room",
                "lights": 4,
                "ceiling_fans": 2,
                "dining_table": 1,
                "sofa": 1,
                "storage": 1,
                "decorations": 2
            },
            follow_redirects=True
        )
        self.assertEqual(post_res.status_code, 200)
        self.assertIn("Budget Allocation Breakdown", post_res.text)
        self.assertIn("Curated Product Recommendations", post_res.text)
        # Check retailer button exists
        self.assertIn("Buy on", post_res.text)

    def test_04_party_planner_flow(self):
        self.client.post("/login", data={"email": "demo@pocketsmart.ai", "password": "demo1234"})
        
        get_res = self.client.get("/planner/party")
        self.assertEqual(get_res.status_code, 200)
        self.assertIn("Party Budget Planner", get_res.text)

        post_res = self.client.post(
            "/planner/party",
            data={
                "budget": 35000,
                "guest_count": 50,
                "event_type": "Birthday",
                "venue": "Home / Backyard",
                "food_pref": "Buffet Dinner + Starters",
                "decor_pref": "Minimalist Pastel & Balloon Garland"
            },
            follow_redirects=True
        )
        self.assertEqual(post_res.status_code, 200)
        self.assertIn("Estimated Total", post_res.text)
        self.assertIn("Catering", post_res.text)

    def test_05_jewelry_planner_flow(self):
        self.client.post("/login", data={"email": "demo@pocketsmart.ai", "password": "demo1234"})
        
        get_res = self.client.get("/planner/jewelry")
        self.assertEqual(get_res.status_code, 200)
        self.assertIn("Jewelry Budget Planner", get_res.text)

        post_res = self.client.post(
            "/planner/jewelry",
            data={
                "budget": 30000,
                "occasion": "Wedding",
                "jewelry_type": "All",
                "preferred_style": "Traditional",
                "color_pref": "Gold"
            },
            follow_redirects=True
        )
        self.assertEqual(post_res.status_code, 200)
        self.assertIn("Within Budget", post_res.text)

    def test_06_history_page(self):
        self.client.post("/login", data={"email": "demo@pocketsmart.ai", "password": "demo1234"})
        
        res = self.client.get("/history")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Recommendation History", res.text)
        self.assertIn("history-table", res.text)

    def test_07_static_assets(self):
        css_res = self.client.get("/static/css/styles.css")
        self.assertEqual(css_res.status_code, 200)
        self.assertIn("#2563EB", css_res.text)
        self.assertNotIn("linear-gradient", css_res.text)

        js_res = self.client.get("/static/js/main.js")
        self.assertEqual(js_res.status_code, 200)

    def test_08_api_generate_routes(self):
        # JSON API: generate-home
        res_home = self.client.post(
            "/generate-home",
            json={"budget": 45000, "room_type": "Bedroom", "items": {"storage": 1, "lights": 2}},
            headers={"Accept": "application/json"}
        )
        self.assertEqual(res_home.status_code, 200)
        data = res_home.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("items", data["data"])

        # JSON API: generate-party
        res_party = self.client.post(
            "/generate-party",
            json={"budget": 25000, "guest_count": 30, "event_type": "Anniversary"},
            headers={"Accept": "application/json"}
        )
        self.assertEqual(res_party.status_code, 200)
        self.assertEqual(res_party.json()["status"], "success")

        # JSON API: generate-jewelry
        res_jewel = self.client.post(
            "/generate-jewelry",
            json={"budget": 20000, "occasion": "Daily Wear", "preferred_style": "Minimalist"},
            headers={"Accept": "application/json"}
        )
        self.assertEqual(res_jewel.status_code, 200)
        self.assertEqual(res_jewel.json()["status"], "success")

    def test_09_jwt_and_session_endpoints(self):
        # Token issue
        res_token = self.client.post("/token", json={"email": "demo@pocketsmart.ai", "password": "demo1234"})
        self.assertEqual(res_token.status_code, 200)
        token_data = res_token.json()
        self.assertIn("access_token", token_data)
        token = token_data["access_token"]

        # Session info with Bearer token
        res_info = self.client.get("/session-info", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_info.status_code, 200)
        info_data = res_info.json()
        self.assertTrue(info_data["is_authenticated"])
        self.assertEqual(info_data["email"], "demo@pocketsmart.ai")

        # Session data
        res_data = self.client.get("/session-data", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_data.status_code, 200)
        self.assertIn("metrics", res_data.json())

    def test_10_recommendations_details_and_health(self):
        # Details endpoint
        res_details = self.client.get("/recommendations-details?category=home&budget=50000")
        self.assertEqual(res_details.status_code, 200)
        self.assertEqual(res_details.json()["status"], "success")

        # Startup / health endpoint
        res_health = self.client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        health_data = res_health.json()
        self.assertEqual(health_data["status"], "online")
        self.assertTrue(health_data["database_connected"])
        self.assertIn("Amazon", health_data["supported_platforms"])

if __name__ == "__main__":
    unittest.main()
