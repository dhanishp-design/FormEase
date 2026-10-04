import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestFormEaseBackend(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")

    def test_demo_analyze_endpoint(self):
        response = self.client.post("/api/analyze", data={"is_demo": "true", "language": "en"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_demo"])
        self.assertEqual(len(data["fields"]), 12)
        # Check Annual Family Income field exists
        income_field = next((f for f in data["fields"] if f["id"] == "field_003"), None)
        self.assertIsNotNone(income_field)
        self.assertEqual(income_field["name"], "Annual Family Income")
        self.assertTrue(income_field["required"])

    def test_invalid_file_extension(self):
        fake_exe = ("malicious.exe", b"binarycontent", "application/octet-stream")
        response = self.client.post("/api/analyze", files={"file": fake_exe})
        self.assertEqual(response.status_code, 400)
        self.assertIn("isn't supported", response.json()["detail"].lower())

    def test_explain_field(self):
        response = self.client.post("/api/explain", json={"field_id": "field_003", "language": "en"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["field_id"], "field_003")
        self.assertIn("income", data["explanation"].lower())

    def test_explain_field_marathi(self):
        response = self.client.post("/api/explain", json={"field_id": "field_003", "language": "mr"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["language"], "mr")
        self.assertIn("उत्पन्न", data["explanation"])

    def test_help_fill_annual_income_calc(self):
        # Step 0: Father income
        payload = {
            "field_id": "field_003",
            "current_step": 4,  # Calculation step
            "answers": {
                "father_income": "30000",
                "mother_has_income": "Yes",
                "mother_income": "10000",
                "other_annual_income": "0"
            },
            "language": "en"
        }
        response = self.client.post("/api/help-fill", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_completed"])
        # Father: 30k*12 = 3.6L, Mother: 10k*12 = 1.2L => Total = ₹4,80,000
        self.assertEqual(data["suggested_value"], "₹4,80,000")
        self.assertIn("Father", data["calculation_breakdown"])
        self.assertIn("Mother", data["calculation_breakdown"])

    def test_chat_endpoint(self):
        response = self.client.post("/api/chat", json={
            "message": "What does domicile mean?",
            "language": "en"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("permanent resident", data["reply"].lower())
        self.assertTrue(len(data["suggested_questions"]) > 0)

if __name__ == "__main__":
    unittest.main()
