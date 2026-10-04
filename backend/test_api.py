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
        income_field = next((f for f in data["fields"] if f["id"] == "field_003"), None)
        self.assertIsNotNone(income_field)
        self.assertEqual(income_field["name"], "Annual Family Income")
        self.assertTrue(income_field["required"])
        # Verify source-of-truth metadata is present
        self.assertIn("preceding financial year", income_field["what_document_says"].lower())
        self.assertIn("inr", income_field["what_document_says"].lower())

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
        self.assertIn("inr", data["what_document_says"].lower())

    def test_explain_field_marathi(self):
        response = self.client.post("/api/explain", json={"field_id": "field_003", "language": "mr"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["language"], "mr")
        self.assertIn("उत्पन्न", data["explanation"])

    def test_help_fill_annual_income_calc(self):
        payload = {
            "field_id": "field_003",
            "current_step": 4,
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
        self.assertEqual(data["suggested_value"], "₹4,80,000")
        self.assertIn("Father", data["calculation_breakdown"])
        self.assertIn("Mother", data["calculation_breakdown"])

    # CRITICAL TEST 34: User asks "What should I enter?" for Annual Family Income
    def test_critical_test_34_document_source_of_truth_income(self):
        response = self.client.post("/api/chat", json={
            "message": "What should I enter?",
            "selected_field_id": "field_003",
            "language": "en"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Must mention previous financial year and INR, NOT "current annual salary"
        self.assertIn("previous financial year", data["reply"].lower())
        self.assertIn("inr", data["reply"].lower())
        self.assertNotIn("current annual salary", data["reply"].lower())

    # CRITICAL TEST 35: Age validation against document range 18-35 years
    def test_critical_test_35_age_validation(self):
        payload = {
            "field_id": "field_002",
            "current_step": 1,
            "answers": {
                "birth_date": "17"  # Under 18 years
            },
            "language": "en"
        }
        response = self.client.post("/api/help-fill", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["verification_warning"])
        self.assertIn("18–35", data["verification_warning"])

    # CRITICAL TEST 36: Dependency handling when mother has no income
    def test_critical_test_36_dependency_handling(self):
        payload = {
            "field_id": "field_003",
            "current_step": 1,
            "answers": {
                "father_income": "30000",
                "mother_has_income": "No"
            },
            "language": "en"
        }
        response = self.client.post("/api/help-fill", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Next step should skip asking for mother's income and provide dependency explanation
        self.assertIsNotNone(data["document_guidance"])
        self.assertIn("applies when you select YES", data["document_guidance"])

    # CRITICAL TEST 37: Mobile number format validation (10 digits)
    def test_critical_test_37_mobile_format_validation(self):
        payload = {
            "field_id": "field_006",
            "current_step": 1,
            "answers": {
                "phone_number": "12345"  # invalid length
            },
            "language": "en"
        }
        response = self.client.post("/api/help-fill", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["verification_warning"])
        self.assertIn("10-digit", data["verification_warning"])

    def test_chat_endpoint(self):
        response = self.client.post("/api/chat", json={
            "message": "What does domicile mean?",
            "language": "en"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("permanent resident", data["reply"].lower())
        self.assertTrue(len(data["suggested_questions"]) > 0)

    def test_nemotron_health_status(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nemotron_configured", data)
        self.assertIn("nemotron_model", data)
        self.assertIn("nemotron-3.5-lightning", data["nemotron_model"])
        self.assertTrue(data["nemotron_configured"])

    def test_pdf_text_extraction(self):
        import io, pypdf
        from backend.ai_service import ai_service
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=200, height=200)
        buf = io.BytesIO()
        writer.write(buf)
        buf.seek(0)
        pdf_bytes = buf.getvalue()
        # Should execute safely without error
        text = ai_service.extract_text_from_document(pdf_bytes, filename="form.pdf", mime_type="application/pdf")
        self.assertIsInstance(text, str)

if __name__ == "__main__":
    unittest.main()

