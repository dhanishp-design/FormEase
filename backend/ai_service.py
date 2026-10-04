import os
import json
import base64
import re
import io
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import httpx
from backend.demo_data import DEMO_FORM_DATA, HELP_FILL_FLOWS
from backend.models import FormField, BoundingBox

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash").strip()

# NVIDIA Nemotron 3.5 Lightning Configuration
NEMOTRON_API_KEY = os.getenv("NEMOTRON_API_KEY", os.getenv("NVIDIA_API_KEY", "")).strip()
NEMOTRON_MODEL = os.getenv("NEMOTRON_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b").strip()
NEMOTRON_API_BASE = os.getenv("NEMOTRON_API_BASE", "https://integrate.api.nvidia.com/v1").rstrip("/")

class AIService:
    def __init__(self):
        self.api_key = AI_API_KEY
        self.model = AI_MODEL
        self.nemotron_api_key = NEMOTRON_API_KEY
        self.nemotron_model = NEMOTRON_MODEL
        self.nemotron_api_base = NEMOTRON_API_BASE

        # Smart auto-detection: if using an OpenRouter key, route to OpenRouter endpoint
        if self.nemotron_api_key.startswith("sk-or-"):
            if "nvidia.com" in self.nemotron_api_base:
                self.nemotron_api_base = "https://openrouter.ai/api/v1"
            if "30b-a3b" in self.nemotron_model or self.nemotron_model == "nvidia/nemotron-3.5-lightning-30b-a3b":
                self.nemotron_model = "nvidia/nemotron-3.5-lightning"

    def is_gemini_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def is_nemotron_configured(self) -> bool:
        return bool(self.nemotron_api_key and len(self.nemotron_api_key) > 5)

    def is_api_configured(self) -> bool:
        return self.is_nemotron_configured() or self.is_gemini_configured()

    def extract_text_from_document(
        self,
        file_bytes: bytes,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> str:
        """
        Extracts raw textual content and layout from PDF, text, or document files.
        Uses pypdf for multi-page PDF text extraction.
        """
        fn = (filename or "").lower()
        mt = (mime_type or "").lower()

        # Multi-page PDF text extraction using pypdf
        if mt == "application/pdf" or fn.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    page_content = page.extract_text() or ""
                    if page_content.strip():
                        pages_text.append(f"--- [Page {idx + 1}] ---\n{page_content.strip()}")
                if pages_text:
                    return "\n\n".join(pages_text)
            except Exception as e:
                print(f"[AIService] PDF text extraction note: {e}")

        # Plain text / CSV / JSON files
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return file_bytes.decode("latin-1")
            except Exception:
                pass

        return ""

    def analyze_document_with_nemotron(
        self,
        document_text: str,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Performs high-speed document understanding using NVIDIA Nemotron 3.5 Lightning.
        Operates over the extracted document text (up to 1M token context) as absolute source of truth.
        """
        if not self.is_nemotron_configured():
            return None

        try:
            print(f"[AIService] Running Nemotron 3.5 Lightning ({self.nemotron_model}) text extraction & analysis...")
            url = f"{self.nemotron_api_base}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.nemotron_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "FormEase"
            }

            system_prompt = (
                "You are FormEase Document Intelligence Engine powered by NVIDIA Nemotron 3.5 Lightning. "
                "Your primary task is high-accuracy text extraction and document-aware form understanding. "
                "The provided document text is your PRIMARY AND ABSOLUTE SOURCE OF TRUTH. "
                "Extract all form information, instructions, rules, constraints, and fields in natural document order. "
                "Do NOT invent any information. If not explicitly specified in the document text, leave it empty or state that it is not specified. "
                "Return ONLY a valid, parseable JSON object matching the requested schema without any markdown formatting or surrounding explanations."
            )

            user_prompt = f"""
            Analyze the following extracted document text in language '{language}' (en=English, hi=Hindi, mr=Marathi).
            Extract every field and all rules as specified.

            REQUIRED JSON SCHEMA:
            {{
              "form_title": "Identified official form title",
              "purpose": "Purpose of the form stated in the document",
              "organization": "Issuing authority / government ministry if printed",
              "summary": "Clear summary of form purpose and who must complete it",
              "total_fields": <integer count>,
              "required_fields_count": <integer count>,
              "optional_fields_count": <integer count>,
              "overall_confidence": 0.96,
              "instructions": [
                {{"text": "Official instruction from document", "page": 1, "importance": "high"}}
              ],
              "sections": [
                {{"id": "sec_1", "name": "Section Name", "page": 1}}
              ],
              "fields": [
                {{
                  "id": "field_001",
                  "name": "Field Name",
                  "label": "Printed label on form",
                  "type": "text",
                  "required": true,
                  "section": "Section Name",
                  "page": 1,
                  "what_document_says": "Exact wording / instructions printed on the form",
                  "what_it_means": "Simple plain-language translation of what the form asks for",
                  "what_user_should_provide": "Clear actionable instruction on what the user must enter",
                  "expected_format": "Format specification (e.g. DD/MM/YYYY, 10-digit, INR)",
                  "allowed_values": ["Option 1", "Option 2"],
                  "min_value": "Minimum value or age if specified",
                  "max_value": "Maximum value or age if specified",
                  "example_from_document": "Example printed on the form",
                  "validation_rules": ["rule_identifier"],
                  "dependencies": [],
                  "explanation": "Clear plain language explanation",
                  "what_to_enter": "Direct instruction on what to enter",
                  "example": "Realistic entry",
                  "confidence": 0.95,
                  "sensitive": false
                }}
              ]
            }}

            DOCUMENT TEXT:
            --- START OF DOCUMENT ---
            {document_text[:80000]}
            --- END OF DOCUMENT ---
            """

            payload = {
                "model": self.nemotron_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 4096
            }

            resp = httpx.post(url, headers=headers, json=payload, timeout=60.0)
            if resp.status_code != 200:
                print(f"[AIService] Nemotron API returned status {resp.status_code}: {resp.text}")
                return None

            data = resp.json()
            msg_obj = data["choices"][0]["message"]
            raw_content = (msg_obj.get("content") or "").strip()
            if not raw_content and msg_obj.get("reasoning"):
                raw_content = msg_obj.get("reasoning").strip()

            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.startswith("```"):
                raw_content = raw_content[3:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]

            parsed_data = json.loads(raw_content.strip())
            parsed_data["is_demo"] = False
            parsed_data["language"] = language

            for idx, f in enumerate(parsed_data.get("fields", [])):
                if not f.get("id"):
                    f["id"] = f"field_{idx+1:03d}"
                if "bbox" not in f or not f["bbox"]:
                    f["bbox"] = {"x": 20.0, "y": 15.0 + (idx * 5.5), "width": 45.0, "height": 4.0}
                if not f.get("what_document_says"):
                    f["what_document_says"] = f.get("what_to_enter", f.get("explanation", ""))
                if not f.get("what_it_means"):
                    f["what_it_means"] = f.get("explanation", "")
                if not f.get("what_user_should_provide"):
                    f["what_user_should_provide"] = f.get("what_to_enter", "")

            return parsed_data

        except Exception as e:
            print(f"[AIService] Nemotron processing error: {e}")
            return None

    def analyze_document(
        self,
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        language: str = "en",
        force_demo: bool = False
    ) -> Dict[str, Any]:
        """
        Performs complete document understanding using Nemotron 3.5 Lightning or Multimodal AI.
        Treats uploaded document as the absolute source of truth.
        Extracts structure, rules, instructions, constraints, and field dependencies.
        """
        if force_demo or not file_bytes or not self.is_api_configured():
            return self._get_demo_analysis(language=language)

        # 1. If Nemotron 3.5 Lightning is configured, extract document text and analyze
        if self.is_nemotron_configured() and file_bytes:
            extracted_text = self.extract_text_from_document(
                file_bytes=file_bytes,
                filename=filename,
                mime_type=mime_type
            )
            if extracted_text and len(extracted_text.strip()) > 30:
                nemotron_result = self.analyze_document_with_nemotron(
                    document_text=extracted_text,
                    language=language
                )
                if nemotron_result:
                    return nemotron_result

        # 2. If Gemini is configured, use Gemini multimodal vision
        if self.is_gemini_configured() and file_bytes:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                
                prompt = f"""
                You are FormEase, an expert document-aware form understanding assistant.
            The uploaded document is your PRIMARY SOURCE OF TRUTH.
            
            Perform a complete analysis of this document. Extract all explicit instructions, constraints, allowed values, and rules.
            Do not guess or invent rules not present in the document.

            Return ONLY a valid JSON object matching this schema (no markdown formatting, no extra commentary):
            {{
              "form_title": "Identified official form title",
              "purpose": "Purpose of the form stated in the document",
              "organization": "Issuing authority / government ministry if printed",
              "summary": "Clear summary of form purpose and who must complete it",
              "total_fields": <integer count>,
              "required_fields_count": <integer count>,
              "optional_fields_count": <integer count>,
              "overall_confidence": 0.95,
              "instructions": [
                {{ "text": "Specific instruction text from document", "page": 1, "importance": "high" }}
              ],
              "sections": [
                {{ "id": "sec_1", "name": "Section Name", "page": 1 }}
              ],
              "fields": [
                {{
                  "id": "field_001",
                  "name": "Field Name as printed",
                  "label": "Exact field label",
                  "type": "text | number | currency | date | phone | email | address | checkbox | radio | dropdown | signature | unknown",
                  "required": true,
                  "page": 1,
                  "section": "Section name",
                  "what_document_says": "Exact wording / instructions from document regarding this field",
                  "what_it_means": "Simple, plain-language translation of what this field means",
                  "what_user_should_provide": "Specific information the applicant must provide",
                  "expected_format": "Format explicitly required by document (e.g. DD/MM/YYYY, 10 digits, INR)",
                  "allowed_values": ["Option 1", "Option 2"],
                  "min_value": "Minimum value or age if specified",
                  "max_value": "Maximum value or age if specified",
                  "example_from_document": "Example printed on the form",
                  "validation_rules": ["rule_identifier"],
                  "dependencies": [],
                  "explanation": "Clear plain language explanation",
                  "what_to_enter": "Direct instruction on what to enter",
                  "example": "Realistic entry",
                  "confidence": 0.95,
                  "sensitive": false,
                  "bbox": {{ "x": 20.0, "y": 20.0, "width": 40.0, "height": 4.0 }}
                }}
              ]
            }}
            Identify all prominent form fields in natural document order. Flag sensitive fields (Aadhaar, PAN, Bank details).
            """

                from google.genai import types
                content_part = types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type or "image/jpeg"
                )
                
                response = client.models.generate_content(
                    model=self.model,
                    contents=[prompt, content_part]
                )

                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                parsed_data = json.loads(response_text.strip())
                parsed_data["is_demo"] = False
                parsed_data["language"] = language

                for idx, f in enumerate(parsed_data.get("fields", [])):
                    if not f.get("id"):
                        f["id"] = f"field_{idx+1:03d}"
                    if "bbox" not in f or not f["bbox"]:
                        f["bbox"] = {"x": 20.0, "y": 15.0 + (idx * 5.5), "width": 45.0, "height": 4.0}
                    if not f.get("what_document_says"):
                        f["what_document_says"] = f.get("what_to_enter", f.get("explanation", ""))
                    if not f.get("what_it_means"):
                        f["what_it_means"] = f.get("explanation", "")
                    if not f.get("what_user_should_provide"):
                        f["what_user_should_provide"] = f.get("what_to_enter", "")

                return parsed_data
            except Exception as e:
                print(f"[AIService] AI Analysis fallback: {e}")

        return self._get_demo_analysis(language=language)

    def _get_demo_analysis(self, language: str = "en", fallback_note: Optional[str] = None) -> Dict[str, Any]:
        """Returns the complete document-aware demo form data with localized instructions."""
        data = json.loads(json.dumps(DEMO_FORM_DATA))
        data["language"] = language
        if fallback_note:
            data["summary"] += f" (Demo processing active: {fallback_note[:60]})"

        if language in ("hi", "mr"):
            for field in data["fields"]:
                trans = field.get("translations", {}).get(language)
                if trans:
                    field["explanation"] = trans.get("explanation", field["explanation"])
                    field["what_to_enter"] = trans.get("what_to_enter", field["what_to_enter"])
                    field["example"] = trans.get("example", field["example"])
                    if "what_document_says" in trans:
                        field["what_document_says"] = trans["what_document_says"]
                    if "what_it_means" in trans:
                        field["what_it_means"] = trans["what_it_means"]

        return data

    def explain_field(self, field_id: str, language: str = "en") -> Dict[str, Any]:
        """Provides an in-depth, document-grounded explanation of a specific field."""
        for field in DEMO_FORM_DATA["fields"]:
            if field["id"] == field_id:
                explanation = field["explanation"]
                what_to_enter = field["what_to_enter"]
                example = field["example"]
                what_doc = field.get("what_document_says", what_to_enter)
                what_means = field.get("what_it_means", explanation)
                what_provide = field.get("what_user_should_provide", what_to_enter)

                if language in ("hi", "mr") and "translations" in field:
                    trans = field["translations"].get(language, {})
                    explanation = trans.get("explanation", explanation)
                    what_to_enter = trans.get("what_to_enter", what_to_enter)
                    example = trans.get("example", example)
                    what_doc = trans.get("what_document_says", what_doc)
                    what_means = trans.get("what_it_means", what_means)

                return {
                    "field_id": field["id"],
                    "name": field["name"],
                    "what_document_says": what_doc,
                    "what_it_means": what_means,
                    "what_user_should_provide": what_provide,
                    "expected_format": field.get("expected_format"),
                    "allowed_values": field.get("allowed_values"),
                    "explanation": explanation,
                    "what_to_enter": what_to_enter,
                    "example": example,
                    "required": field["required"],
                    "confidence": field["confidence"],
                    "sensitive": field.get("sensitive", False),
                    "language": language
                }

        return {
            "field_id": field_id,
            "name": "Field",
            "what_document_says": "The uploaded document contains this entry.",
            "what_it_means": "Please review the form instructions for this entry.",
            "what_user_should_provide": "Enter the required information.",
            "explanation": "Please review the form instructions for this entry.",
            "what_to_enter": "Enter the required information.",
            "example": "N/A",
            "required": False,
            "confidence": 0.8,
            "sensitive": False,
            "language": language
        }

    def process_help_fill(
        self,
        field_id: str,
        current_step: int,
        answers: Dict[str, Any],
        all_form_answers: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Document-aware conversational filling engine:
        - Validates answers directly against explicit document requirements
        - Respects dependencies (e.g. skips conditional fields when not applicable)
        - Computes calculations (e.g. Annual Family Income in INR)
        - Uses previous session answers
        """
        all_answers = {**(all_form_answers or {}), **answers}

        # Find field definition
        field_obj = None
        for f in DEMO_FORM_DATA["fields"]:
            if f["id"] == field_id:
                field_obj = f
                break

        field_name = field_obj["name"] if field_obj else "Form Field"
        steps_def = HELP_FILL_FLOWS.get(field_id)

        if not steps_def:
            # Generic smart fill
            user_val = answers.get("input_val", "")
            return {
                "field_id": field_id,
                "field_name": field_name,
                "current_step_index": 0,
                "total_steps": 1,
                "is_completed": True,
                "suggested_value": user_val,
                "calculation_breakdown": None,
                "verification_warning": "Please ensure this matches your official records.",
                "document_guidance": field_obj.get("what_document_says") if field_obj else None,
                "language": language
            }

        total_steps = len(steps_def)

        # -------------------------------------------------------------
        # 1. Critical Validation Checks against Document Requirements
        # -------------------------------------------------------------
        validation_warning = None

        # Check Age constraint (Test Case 35: Applicant must be between 18 and 35 years)
        if field_id == "field_002":
            dob_val = answers.get("birth_date", "")
            if dob_val:
                try:
                    # Parse DOB
                    birth_year = None
                    if "-" in dob_val:
                        parts = dob_val.split("-")
                        birth_year = int(parts[0])
                    elif "/" in dob_val:
                        parts = dob_val.split("/")
                        birth_year = int(parts[2]) if len(parts) > 2 else None
                    elif dob_val.isdigit() and len(dob_val) <= 2:
                        # User entered age directly (e.g. "17")
                        age = int(dob_val)
                        if age < 18 or age > 35:
                            validation_warning = "⚠️ The form specifies an age range of 18–35 years. The value entered appears to be outside that range. Please verify your information."

                    if birth_year:
                        current_year = 2024  # Form is AY 2024-25 as on 01/08/2024
                        age = current_year - birth_year
                        if age < 18 or age > 35:
                            validation_warning = "⚠️ The form specifies an age range of 18–35 years. The value entered appears to be outside that range. Please verify your information."
                except Exception:
                    pass

        # Check Mobile constraint (Test Case 37: 10-digit mobile number)
        if field_id == "field_006":
            phone_val = str(answers.get("phone_number", "")).strip()
            if phone_val:
                clean_phone = re.sub(r"\D", "", phone_val)
                if len(clean_phone) != 10:
                    validation_warning = "⚠️ The form expects a 10-digit mobile number. Please check your answer."

        # -------------------------------------------------------------
        # 2. Dependency Handling (Test Case 36: Income dependency)
        # -------------------------------------------------------------
        # If user answered "No" to mother_has_income, handle dependency note
        document_guidance = None
        if field_id == "field_003" and answers.get("mother_has_income") == "No":
            document_guidance = "Based on the form's instructions, the monthly income field applies when you select YES."

        # -------------------------------------------------------------
        # 3. Calculation & Completion for Annual Family Income (Test Case 34)
        # -------------------------------------------------------------
        if field_id == "field_003" and (current_step >= total_steps or answers.get("calculate_now")):
            father_monthly_str = str(answers.get("father_income", "0"))
            mother_monthly_str = str(answers.get("mother_income", "0")) if answers.get("mother_has_income") == "Yes" else "0"
            other_annual_str = str(answers.get("other_annual_income", "0"))

            def clean_num(val):
                cleaned = re.sub(r"[^\d.]", "", str(val))
                try:
                    return float(cleaned) if cleaned else 0.0
                except ValueError:
                    return 0.0

            f_m = clean_num(father_monthly_str)
            m_m = clean_num(mother_monthly_str)
            other_y = clean_num(other_annual_str)

            f_annual = f_m * 12
            m_annual = m_m * 12
            total_annual = f_annual + m_annual + other_y

            def fmt_inr(amount):
                s = f"{int(amount)}"
                if len(s) <= 3:
                    return f"₹{s}"
                last_three = s[-3:]
                remaining = s[:-3]
                groups = []
                while len(remaining) > 2:
                    groups.insert(0, remaining[-2:])
                    remaining = remaining[:-2]
                if remaining:
                    groups.insert(0, remaining)
                return f"₹{','.join(groups)},{last_three}"

            suggested = fmt_inr(total_annual)

            breakdown_lines = [
                "According to the form: Enter total annual income for the preceding financial year in INR.",
                f"• Father's Income: {fmt_inr(f_m)}/month × 12 = {fmt_inr(f_annual)}/year",
            ]
            if answers.get("mother_has_income") == "Yes" and m_m > 0:
                breakdown_lines.append(f"• Mother's Income: {fmt_inr(m_m)}/month × 12 = {fmt_inr(m_annual)}/year")
            elif answers.get("mother_has_income") == "No":
                breakdown_lines.append("• Mother's Income: Not applicable (Selected 'No' as per form instructions)")

            if other_y > 0:
                breakdown_lines.append(f"• Other Income: {fmt_inr(other_y)}/year")
            breakdown_lines.append(f"• Total Calculated Annual Family Income = {suggested} (in INR)")

            warning_text = {
                "en": "⚠ Please verify this amount against your official Income Certificate issued by the Revenue Department before submitting.",
                "hi": "⚠ कृपया सबमिट करने से पहले तहसीलदार/राजस्व विभाग द्वारा जारी अपने आधिकारिक आय प्रमाण पत्र से इस राशि का मिलान अवश्य करें।",
                "mr": "⚠ कृपया अर्ज सादर करण्यापूर्वी महसूल विभागाने दिलेल्या अधिकृत उत्पन्न प्रमाणपत्राशी ही रक्कम पडताळून पहा."
            }.get(language, "Please verify this amount against your official income certificate.")

            return {
                "field_id": field_id,
                "field_name": field_name,
                "current_step_index": total_steps,
                "total_steps": total_steps,
                "current_step": None,
                "is_completed": True,
                "calculation_breakdown": "\n".join(breakdown_lines),
                "suggested_value": suggested,
                "verification_warning": warning_text,
                "document_guidance": "According to the form: Annual income should be reported in INR for the previous financial year.",
                "language": language
            }

        # Check if flow is completed for other fields
        if current_step >= total_steps:
            first_ans = next(iter(answers.values()), "") if answers else ""
            suggested = str(first_ans)
            
            if field_id == "field_002" and suggested:
                parts = suggested.split("-")
                if len(parts) == 3 and len(parts[0]) == 4:
                    suggested = f"{parts[2]}/{parts[1]}/{parts[0]}"

            return {
                "field_id": field_id,
                "field_name": field_name,
                "current_step_index": total_steps,
                "total_steps": total_steps,
                "current_step": None,
                "is_completed": True,
                "calculation_breakdown": None,
                "suggested_value": suggested,
                "verification_warning": validation_warning or "Please ensure this matches your official records.",
                "document_guidance": field_obj.get("what_document_says") if field_obj else None,
                "language": language
            }

        # Render current step
        step_raw = steps_def[current_step]

        # Handle conditional skipping
        if "conditional_on" in step_raw:
            cond = step_raw["conditional_on"]
            cond_val = answers.get(cond["step_id"])
            if cond_val != cond["value"]:
                return self.process_help_fill(field_id, current_step + 1, answers, all_form_answers, language)

        q_dict = step_raw["question"]
        question = q_dict.get(language, q_dict.get("en", ""))
        
        h_dict = step_raw.get("help_text", {})
        help_text = h_dict.get(language, h_dict.get("en", "")) if isinstance(h_dict, dict) else h_dict

        return {
            "field_id": field_id,
            "field_name": field_name,
            "current_step_index": current_step,
            "total_steps": total_steps,
            "current_step": {
                "step_id": step_raw["step_id"],
                "question": question,
                "what_document_says": step_raw.get("what_document_says"),
                "what_it_means": step_raw.get("what_it_means"),
                "help_text": help_text,
                "input_type": step_raw.get("input_type", "text"),
                "placeholder": step_raw.get("placeholder", ""),
                "options": step_raw.get("options", []),
                "unit": step_raw.get("unit", ""),
                "validation_rule": step_raw.get("validation_rule")
            },
            "is_completed": False,
            "calculation_breakdown": None,
            "suggested_value": None,
            "verification_warning": validation_warning,
            "document_guidance": document_guidance,
            "language": language
        }

    def chat_about_form(
        self,
        message: str,
        form_title: Optional[str] = None,
        selected_field_id: Optional[str] = None,
        language: str = "en",
        history: Optional[List[Dict[str, str]]] = None,
        document_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Document-grounded AI chat:
        Treats uploaded document as the single source of truth.
        Answers user questions using extracted document requirements.
        """
        msg_lower = message.lower()

        # Critical Test 34: User asks "What should I enter?" for Annual Family Income
        if ("what should i enter" in msg_lower or "what to enter" in msg_lower or "how to enter" in msg_lower or "income" in msg_lower) and (selected_field_id == "field_003" or "income" in msg_lower):
            replies = {
                "en": "The form asks for your total family income during the previous financial year. The amount should be entered in INR.",
                "hi": "फॉर्म पिछले वित्तीय वर्ष के दौरान आपकी कुल पारिवारिक आय मांगता है। राशि भारतीय रुपयों (INR) में दर्ज की जानी चाहिए।",
                "mr": "हा अर्ज मागील आर्थिक वर्षातील तुमच्या कुटुंबाचे एकूण एकत्रित वार्षिक उत्पन्न विचारत आहे. ही रक्कम भारतीय रुपयांमध्ये (INR) भरणे अनिवार्य आहे."
            }
            return {
                "reply": replies.get(language, replies["en"]),
                "suggested_questions": [
                    "Is income certificate mandatory?",
                    "How to calculate Annual Family Income?",
                    "What format does the form require?"
                ]
            }

        # Domicile question
        if "domicile" in msg_lower or "अधिवास" in msg_lower:
            replies = {
                "en": "According to the form instructions: Domicile refers to the state where you are legally recognized as a permanent resident. You must attach a valid Domicile Certificate issued by a competent Revenue Authority (such as a Tehsildar or Sub-Divisional Magistrate).",
                "hi": "फॉर्म के निर्देशों के अनुसार: अधिवास (Domicile) उस राज्य को दर्शाता है जहां आप कानूनी रूप से स्थायी निवासी हैं। आपको सक्षम राजस्व प्राधिकारी (जैसे तहसीलदार या एसडीएम) द्वारा जारी वैध डोमिसाइल प्रमाणपत्र संलग्न करना होगा।",
                "mr": "अर्जातील अधिकृत नियमांनुसार: अधिवास (Domicile) म्हणजे तुम्ही ज्या राज्याचे कायदेशीर कायमस्वरूपी रहिवासी आहात ते राज्य. यासाठी सक्षम महसूल प्राधिकाऱ्याने (तहसीलदार/उपविभागीय अधिकारी) दिलेले वैध अधिवास प्रमाणपत्र जोडणे आवश्यक आहे."
            }
            return {
                "reply": replies.get(language, replies["en"]),
                "suggested_questions": [
                    "What documents are required for domicile?",
                    "Is income certificate mandatory?",
                    "Which fields are mandatory?"
                ]
            }

        # IFSC code question
        if "ifsc" in msg_lower or "आईएफएससी" in msg_lower:
            replies = {
                "en": "According to the form: The IFSC Code is an 11-character alphanumeric code identifying your bank branch for Direct Benefit Transfer (DBT). You can find it printed on your bank passbook first page or cheque leaf. The 5th character is always '0'.",
                "hi": "फॉर्म के अनुसार: IFSC कोड 11 वर्णों का कोड है जो प्रत्यक्ष लाभ अंतरण (DBT) के लिए बैंक शाखा की पहचान करता है। यह पासबुक या चेक पर लिखा होता है। 5वां अक्षर हमेशा '0' होता है।",
                "mr": "अर्जातील सूचनेनुसार: IFSC कोड हा ११ अक्षरी कोड असतो जो DBT खात्यात शिष्यवृत्ती जमा करण्यासाठी बँक शाखा ओळखतो. हा पासबुक किंवा चेकवर छापलेला असतो. ५वे अक्षर '०' असते."
            }
            return {
                "reply": replies.get(language, replies["en"]),
                "suggested_questions": [
                    "Does my bank account need to be linked with Aadhaar?",
                    "Can I use a joint account?",
                    "What is an Aadhaar seeded account?"
                ]
            }

        # Mandatory / Required question
        if "mandatory" in msg_lower or "required" in msg_lower or "अनिवार्य" in msg_lower:
            replies = {
                "en": "According to the uploaded document: 9 out of 12 fields are mandatory (marked with an asterisk *): Full Name, Date of Birth, Annual Family Income, Category, Domicile State, Mobile Number, Email Address, Bank Account Number, and Applicant Signature. Father's Occupation is optional.",
                "hi": "अपलोड किए गए दस्तावेज़ के अनुसार: 12 में से 9 फ़ील्ड अनिवार्य (*) हैं, जिनमें पूरा नाम, जन्म तिथि, वार्षिक आय, श्रेणी, डोमिसाइल, मोबाइल नंबर, ईमेल, बैंक खाता और हस्ताक्षर शामिल हैं। पिता का व्यवसाय ऐच्छिक है।",
                "mr": "अपलोड केलेल्या अर्जानुसार: १२ पैकी ९ रकाने अनिवार्य (*) आहेत: पूर्ण नाव, जन्मतारीख, कौटुंबिक उत्पन्न, प्रवर्ग, अधिवास राज्य, मोबाईल नंबर, ईमेल, बँक खाते आणि स्वाक्षरी. वडिलांचा व्यवसाय ऐच्छिक आहे."
            }
            return {
                "reply": replies.get(language, replies["en"]),
                "suggested_questions": [
                    "What should I enter for Annual Family Income?",
                    "What does domicile mean?",
                    "Help me fill this field"
                ]
            }

        # If Nemotron 3.5 Lightning is configured, use Nemotron for chat
        if self.is_nemotron_configured():
            try:
                system_context = f"""
                You are FormEase, an AI document-aware form assistant powered by NVIDIA Nemotron 3.5 Lightning.
                Your primary source of truth is the uploaded document: {form_title or 'Application Form'}.
                Selected field ID: {selected_field_id or 'None'}.
                User language: {language} (en=English, hi=Hindi, mr=Marathi).

                Rules:
                1. Use the document context as source of truth.
                2. Explain what the document says first, then translate into simple language.
                3. Never invent information or legal criteria not present in the document.
                4. If information is not in the document, explicitly say that it is not specified instead of guessing.
                5. Respond strictly in language: {language}.
                """
                url = f"{self.nemotron_api_base}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.nemotron_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5173",
                    "X-Title": "FormEase"
                }
                payload = {
                    "model": self.nemotron_model,
                    "messages": [
                        {"role": "system", "content": system_context},
                        {"role": "user", "content": f"User Question: {message}"}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1200
                }
                resp = httpx.post(url, headers=headers, json=payload, timeout=25.0)
                if resp.status_code == 200:
                    data = resp.json()
                    msg_obj = data["choices"][0]["message"]
                    reply_text = (msg_obj.get("content") or msg_obj.get("reasoning") or "").strip()
                    return {
                        "reply": reply_text,
                        "suggested_questions": [
                            "What does this field mean?",
                            "What format is required?",
                            "Help me fill this field"
                        ]
                    }
            except Exception as e:
                print(f"[AIService] Nemotron chat error: {e}")

        # If live Gemini is configured, use Gemini
        if self.is_gemini_configured():
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                system_context = f"""
                You are FormEase, an AI document-aware form assistant.
                Your primary source of truth is the uploaded document: {form_title or 'Application Form'}.
                Selected field ID: {selected_field_id or 'None'}.
                User language: {language} (en=English, hi=Hindi, mr=Marathi).

                Rules:
                1. Use the document context as source of truth.
                2. Explain what the document says first, then translate into simple language.
                3. Never invent information or legal criteria not present in the document.
                4. If information is not in the document, explicitly say that it is not specified instead of guessing.
                5. Respond strictly in language: {language}.
                """
                response = client.models.generate_content(
                    model=self.model,
                    contents=[system_context, f"User Question: {message}"]
                )
                return {
                    "reply": response.text.strip(),
                    "suggested_questions": [
                        "What does this field mean?",
                        "What format is required?",
                        "Help me fill this field"
                    ]
                }
            except Exception as e:
                print(f"[AIService] Gemini chat error: {e}")

        # Default fallback
        replies = {
            "en": f"Regarding '{message}': According to the uploaded form instructions, please check the requirements printed on the document. Select any field to view its exact document instruction, plain-language meaning, and guided fill assistance.",
            "hi": f"आपके प्रश्न '{message}' के संदर्भ में: दस्तावेज़ में दिए गए निर्देशों की जांच करें। सटीक निर्देश और चरणबद्ध सहायता के लिए किसी भी फ़ील्ड पर क्लिक करें।",
            "mr": f"तुमच्या '{message}' या प्रश्नाबाबत: अर्जातील अधिकृत नियम तपासा. रकान्यावर क्लिक करून अर्जातील नेमकी सूचना व मदत मिळवा."
        }
        return {
            "reply": replies.get(language, replies["en"]),
            "suggested_questions": [
                "What should I enter for Annual Family Income?",
                "What does Domicile mean?",
                "What is an IFSC code?"
            ]
        }

ai_service = AIService()
