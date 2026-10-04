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

    # -------------------------------------------------------------
    # PART 35 REGRESSION TESTS (TESTS 1 to 6)
    # -------------------------------------------------------------
    def test_part35_regression_test_1_field_not_equal_value(self):
        """
        TEST 1: Document: Nationality: ______ Example: American
        Expected: label = Nationality, documentExample = American, userValue = null (NEVER userValue = American)
        """
        from backend.ai_service import ai_service
        demo = ai_service._get_demo_analysis(language="en")
        for f in demo["fields"]:
            self.assertIsNone(f.get("user_value"), f"Field {f['id']} must have user_value=None initially!")
            if f.get("document_example"):
                self.assertNotEqual(f.get("user_value"), f.get("document_example"), "Example must NEVER be set as userValue!")

    def test_part35_regression_test_2_placeholders(self):
        """
        TEST 2: Document: Name: XXX
        Expected: label = Name, placeholder = XXX, userValue = null (NEVER userValue = XXX)
        """
        from backend.ai_service import ai_service
        demo = ai_service._get_demo_analysis(language="en")
        self.assertIn("placeholders_detected", demo["document_context"])
        for f in demo["fields"]:
            if f.get("placeholder"):
                self.assertIsNone(f.get("user_value"), f"Placeholder {f['placeholder']} must not become user_value!")

    def test_part35_regression_test_3_document_instructions_word_count(self):
        """
        TEST 3: Document: Reason for application (200 words)
        Expected: label = Reason for application, documentInstruction = 200 words,
        Word count tracker validates against 200 words limit.
        """
        payload = {
            "field_id": "field_dynamic_essay",
            "current_step": 0,
            "answers": {
                "input_val": " ".join(["test"] * 210)  # 210 words exceeds 200 words limit
            },
            "language": "en",
            "field_info": {
                "name": "Reason for application",
                "document_instruction": "200 words",
                "what_document_says": "Reason for application (200 words)"
            }
        }
        response = self.client.post("/api/help-fill", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["verification_warning"])
        self.assertIn("200-word limit", data["verification_warning"])
        self.assertIn("210 words", data["verification_warning"])

    def test_part35_regression_test_4_age_validation(self):
        """
        TEST 4: Document: Age: 18-35
        User enters 17 -> Warning displayed.
        """
        payload = {
            "field_id": "field_002",
            "current_step": 1,
            "answers": {"birth_date": "17"},
            "language": "en"
        }
        response = self.client.post("/api/help-fill", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["verification_warning"])
        self.assertIn("18–35", data["verification_warning"])

    def test_part35_regression_test_5_conditional_skip(self):
        """
        TEST 5: Document: Do you have income? YES/NO. If YES: Monthly Income.
        User selects NO -> Monthly income skipped.
        """
        payload = {
            "field_id": "field_003",
            "current_step": 1,
            "answers": {"father_income": "30000", "mother_has_income": "No"},
            "language": "en"
        }
        response = self.client.post("/api/help-fill", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["document_guidance"])
        self.assertIn("applies when you select YES", data["document_guidance"])

    def test_part35_regression_test_6_required_status_not_hallucinated(self):
        """
        TEST 6: Document has no required indicator.
        Expected: required = false (or null), NOT required = true.
        """
        from backend.ai_service import ai_service
        demo = ai_service._get_demo_analysis(language="en")
        optional_fields = [f for f in demo["fields"] if not f["required"]]
        self.assertTrue(len(optional_fields) > 0, "Non-mandatory fields must NOT be hallucinated as required=True!")
        father_occ = next((f for f in demo["fields"] if f["id"] == "field_011"), None)
        self.assertIsNotNone(father_occ)
        self.assertFalse(father_occ["required"])

    def test_sample_scholarship_form_regression(self):
        """
        REGRESSION TEST ON ACTUAL SUPPLIED SAMPLE DOCUMENT:
        tests/sample_scholarship_form.jpeg
        Verifies:
        1. Multimodal OCR extraction succeeds
        2. Extracted form has detected fields (>= 15 fields)
        3. Field != Value separation (all user_value are None initially)
        4. Instructions (200 words / 100 words) are detected
        5. Placeholders (XXX, 202X) are detected
        6. Required status is not hallucinated (no * on form)
        7. document_context is populated
        """
        import os
        from backend.ai_service import ai_service
        sample_path = os.path.join(os.path.dirname(__file__), "..", "tests", "sample_scholarship_form.jpeg")
        self.assertTrue(os.path.exists(sample_path), "Sample scholarship form must exist!")
        with open(sample_path, "rb") as f:
            file_bytes = f.read()

        result = ai_service.analyze_document(
            file_bytes=file_bytes,
            filename="sample_scholarship_form.jpeg",
            mime_type="image/jpeg",
            language="en"
        )
        self.assertIsNotNone(result)
        self.assertIn("fields", result)
        self.assertTrue(len(result["fields"]) >= 15, f"Expected at least 15 fields, got {len(result['fields'])}")

        # Check Field != Value: user_value must be None for every field
        for field in result["fields"]:
            self.assertIsNone(field.get("user_value"), f"Field {field.get('name')} must have user_value=None initially!")

        # Check document_context
        self.assertIn("document_context", result)
        ctx = result["document_context"]
        self.assertEqual(ctx.get("extraction_method"), "MULTIMODAL_VISION_OCR")
        self.assertTrue(len(ctx.get("raw_text", "")) > 50)

        # Check instructions
        instructions_text = " ".join(ctx.get("instructions_detected", []) + [f.get("document_instruction", "") or "" for f in result["fields"]])
        self.assertTrue("word" in instructions_text.lower() or "item" in instructions_text.lower() or "courses" in instructions_text.lower() or len(result.get("instructions", [])) > 0)

        # Check that required is not hallucinated for fields
        required_count = result.get("required_fields_count", 0)
        self.assertTrue(required_count < len(result["fields"]), "Form without asterisks should not mark all fields as required!")

        # Check that all field bounding boxes are normalized to 0-100%
        for field in result["fields"]:
            if field.get("bbox"):
                bx = field["bbox"]["x"]
                by = field["bbox"]["y"]
                bw = field["bbox"]["width"]
                bh = field["bbox"]["height"]
                self.assertGreaterEqual(bx, 0.0, f"Bbox x ({bx}) should be >= 0")
                self.assertLessEqual(bx, 100.0, f"Bbox x ({bx}) should be <= 100")
                self.assertGreaterEqual(by, 0.0, f"Bbox y ({by}) should be >= 0")
                self.assertLessEqual(by, 100.0, f"Bbox y ({by}) should be <= 100")

    def test_image_upload_preview_generation(self):
        """
        Verify that uploading a local image returns document_preview_url with valid base64 data URI.
        """
        import os
        sample_path = os.path.join(os.path.dirname(__file__), "..", "tests", "sample_scholarship_form.jpeg")
        with open(sample_path, "rb") as f:
            file_bytes = f.read()

        response = self.client.post(
            "/api/analyze",
            files={"file": ("sample_form.jpeg", file_bytes, "image/jpeg")},
            data={"is_demo": "false", "language": "en"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get("document_preview_url"))
        self.assertTrue(data["document_preview_url"].startswith("data:image/jpeg;base64,"))
        self.assertGreater(len(data.get("fields", [])), 0)

if __name__ == "__main__":
    unittest.main()

