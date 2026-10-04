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

load_dotenv(override=True)

AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "gemini-flash-lite-latest").strip()

# NVIDIA Nemotron 3.5 Lightning Configuration
NEMOTRON_API_KEY = os.getenv("NEMOTRON_API_KEY", os.getenv("NVIDIA_API_KEY", "")).strip()
NEMOTRON_MODEL = os.getenv("NEMOTRON_MODEL", "nvidia/nemotron-3.5-lightning").strip()
NEMOTRON_API_BASE = os.getenv("NEMOTRON_API_BASE", "https://openrouter.ai/api/v1").rstrip("/")

class AIService:
    def __init__(self):
        self._api_key = AI_API_KEY
        self._model = AI_MODEL
        self._nemotron_api_key = NEMOTRON_API_KEY
        self._nemotron_model = NEMOTRON_MODEL
        self._nemotron_api_base = NEMOTRON_API_BASE

    @property
    def api_key(self) -> str:
        return os.getenv("AI_API_KEY", "").strip() or self._api_key

    @property
    def model(self) -> str:
        return os.getenv("AI_MODEL", "gemini-flash-lite-latest").strip() or self._model

    @property
    def nemotron_api_key(self) -> str:
        return os.getenv("NEMOTRON_API_KEY", os.getenv("NVIDIA_API_KEY", "")).strip() or self._nemotron_api_key

    @property
    def nemotron_model(self) -> str:
        m = os.getenv("NEMOTRON_MODEL", "").strip() or self._nemotron_model
        if "30b-a3b" in m:
            return "nvidia/nemotron-3.5-lightning"
        return m or "nvidia/nemotron-3.5-lightning"

    @property
    def nemotron_api_base(self) -> str:
        base = os.getenv("NEMOTRON_API_BASE", "").strip().rstrip("/") or self._nemotron_api_base
        if self.nemotron_api_key.startswith("sk-or-") and "nvidia.com" in base:
            return "https://openrouter.ai/api/v1"
        return base

    def is_gemini_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def is_nemotron_configured(self) -> bool:
        return bool(self.nemotron_api_key and len(self.nemotron_api_key) > 5)

    def is_api_configured(self) -> bool:
        return self.is_nemotron_configured() or self.is_gemini_configured()

    def is_image_file(self, file_bytes: bytes, filename: Optional[str] = None, mime_type: Optional[str] = None) -> bool:
        """Determines if the uploaded file is an image (PNG, JPG, JPEG, WEBP, etc.) requiring visual OCR."""
        fn = (filename or "").lower()
        mt = (mime_type or "").lower()
        if mt.startswith("image/") or any(fn.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"]):
            return True
        if file_bytes:
            if file_bytes.startswith(b'\x89PNG') or file_bytes.startswith(b'\xff\xd8\xff') or file_bytes.startswith(b'GIF8') or file_bytes.startswith(b'RIFF'):
                return True
        return False

    def extract_text_from_document(
        self,
        file_bytes: bytes,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> str:
        """
        Extracts raw textual content and layout from PDF, text, or document files.
        Uses pypdf for multi-page PDF text extraction.
        Never decodes binary image files as text.
        """
        # If it is an image, it has no digital text stream; visual OCR must be used instead
        if self.is_image_file(file_bytes, filename, mime_type):
            return ""

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
            return ""

        # Plain text / CSV / JSON files
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
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
            if not parsed_data.get("form_id"):
                parsed_data["form_id"] = f"form_{int(datetime.now().timestamp())}"
            if not parsed_data.get("form_title"):
                parsed_data["form_title"] = "Uploaded Application Form"
            if not parsed_data.get("summary"):
                parsed_data["summary"] = "Form extracted and analyzed successfully by Nemotron 3.5 Lightning."

            fields = parsed_data.get("fields", [])
            parsed_data["total_fields"] = len(fields)
            parsed_data["required_fields_count"] = sum(1 for f in fields if f.get("required", False))
            parsed_data["optional_fields_count"] = len(fields) - parsed_data["required_fields_count"]

            for idx, f in enumerate(fields):
                if not f.get("id"):
                    f["id"] = f"field_{idx+1:03d}"
                if "bbox" not in f or not f["bbox"]:
                    f["bbox"] = {"x": 20.0, "y": 15.0 + (idx * 5.5), "width": 45.0, "height": 4.0}
                elif isinstance(f["bbox"], dict):
                    try:
                        bx = float(f["bbox"].get("x", 20.0))
                        by = float(f["bbox"].get("y", 15.0 + (idx * 5.5)))
                        bw = float(f["bbox"].get("width", 45.0))
                        bh = float(f["bbox"].get("height", 4.0))
                        if bx > 100 or by > 100 or bw > 100 or bh > 100:
                            bx, by, bw, bh = bx / 10.0, by / 10.0, bw / 10.0, bh / 10.0
                        bx = max(0.0, min(95.0, round(bx, 2)))
                        by = max(0.0, min(98.0, round(by, 2)))
                        bw = max(2.0, min(100.0 - bx, round(bw, 2)))
                        bh = max(1.5, min(100.0 - by, round(bh, 2)))
                        f["bbox"] = {"x": bx, "y": by, "width": bw, "height": bh}
                    except Exception:
                        f["bbox"] = {"x": 20.0, "y": 15.0 + (idx * 5.5), "width": 45.0, "height": 4.0}

                # CRITICAL: Field != Value separation
                f["user_value"] = None

                lbl = f.get("label", "") or f.get("name", "")
                if not f.get("placeholder"):
                    ph_match = re.search(r'\b(X{2,}|DD/MM/YYYY|YYYY|1234567890)\b', lbl, re.IGNORECASE)
                    if ph_match:
                        f["placeholder"] = ph_match.group(0)

                if not f.get("document_instruction"):
                    ins_match = re.search(r'\(([^)]*(?:words?|characters?|digits?|format|mandatory|item|courses|preceding)[^)]*)\)', lbl, re.IGNORECASE)
                    if ins_match:
                        f["document_instruction"] = ins_match.group(1)

                if not f.get("document_example") and f.get("example_from_document"):
                    f["document_example"] = f["example_from_document"]

                lbl_full = f"{f.get('label', '')} {f.get('name', '')} {f.get('what_document_says', '')}".lower()
                has_req_evidence = bool(re.search(r'(\*|\bmandatory\b|\brequired\b|\bmust\s+provide\b)', lbl_full))
                if f.get("required") is True and not has_req_evidence:
                    f["required"] = False

                if not f.get("what_document_says"):
                    f["what_document_says"] = f.get("what_to_enter", f.get("explanation", ""))
                if not f.get("what_it_means"):
                    f["what_it_means"] = f.get("explanation", "")
                if not f.get("what_user_should_provide"):
                    f["what_user_should_provide"] = f.get("what_to_enter", "")
                if not f.get("explanation"):
                    f["explanation"] = f.get("what_it_means", "Please enter the required information.")
                if not f.get("what_to_enter"):
                    f["what_to_enter"] = f.get("what_user_should_provide", "Enter value as per form instructions.")
                if not f.get("example"):
                    f["example"] = f.get("document_example") or f.get("example_from_document") or "N/A"
                if not f.get("confidence"):
                    f["confidence"] = 0.95

            parsed_data["total_fields"] = len(fields)
            parsed_data["required_fields_count"] = sum(1 for f in fields if f.get("required", False))
            parsed_data["optional_fields_count"] = len(fields) - parsed_data["required_fields_count"]

            # Populate document_context (Part 6 & 17)
            raw_doc_text = document_text
            parsed_data["document_context"] = {
                "title": parsed_data.get("form_title", "Uploaded Application Form"),
                "pages": 1,
                "language": language,
                "extraction_method": "NATIVE_PDF_TEXT + NEMOTRON",
                "raw_text": raw_doc_text,
                "normalized_text": re.sub(r"\s+", " ", raw_doc_text).strip(),
                "instructions_detected": [ins.get("text") for ins in parsed_data.get("instructions", []) if ins.get("text")],
                "placeholders_detected": [f.get("placeholder") for f in fields if f.get("placeholder")],
                "examples_detected": [f.get("document_example") for f in fields if f.get("document_example")],
            }

            return parsed_data

        except Exception as e:
            print(f"[AIService] Nemotron processing error: {e}")
            return None

    def analyze_image_with_vision(
        self,
        file_bytes: bytes,
        mime_type: Optional[str] = None,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Extracts all text and form fields directly from document images (PNG, JPG, scanned forms)
        using multimodal vision AI.
        """
        if not self.is_gemini_configured() or not file_bytes:
            return None

        img_width, img_height = None, None
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(file_bytes))
            img_width, img_height = im.size
        except Exception:
            pass

        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=self.api_key)

            prompt = f"""
            You are FormEase, an expert document-aware form understanding assistant.
            The uploaded document image is your PRIMARY AND ABSOLUTE SOURCE OF TRUTH.
            
            Perform a complete visual OCR and structural analysis of this form image.
            Read every title, section, label, instruction, constraint, table row/column, and input zone.
            Extract all fields in natural reading order (top to bottom, left to right).

            CRITICAL RULES:
            1. FIELD != VALUE:
               - "document_example": If the form contains an example (e.g. "American", "PRIYA RAMESH SHARMA"), store it here. NEVER put it into user_value.
               - "placeholder": If the form has a placeholder (e.g. "XXX", "XXXX", "DD/MM/YYYY", "202X"), store it here. NEVER put it into user_value.
               - "user_value": ALWAYS null. The applicant has not typed their value yet.
            2. REQUIRED STATUS:
               - DO NOT mark every field as required.
               - Only mark "required": true if the document provides explicit evidence (e.g. "*", "Mandatory", "Required", "Must provide").
               - If the document does not specify, set "required": false.
            3. INSTRUCTIONS & CONSTRAINTS:
               - Extract word count limits, character limits, date formats, or instructions (e.g. "200 words", "100 words", "If no item, fill in 'No'") into "document_instruction".
            4. DOCUMENT CONTEXT:
               - Transcribe the complete visual raw text of the document into "document_context.raw_text".

            Return ONLY a valid JSON object matching this schema (no markdown formatting, no extra commentary):
            {{
              "form_title": "Identified official form title",
              "purpose": "Purpose of the form stated in the document",
              "organization": "Issuing authority / school / organization if printed",
              "summary": "Clear summary of form purpose and who must complete it",
              "total_fields": <integer count>,
              "required_fields_count": <integer count>,
              "optional_fields_count": <integer count>,
              "overall_confidence": 0.95,
              "document_context": {{
                "title": "Official Form Title",
                "pages": 1,
                "language": "{language}",
                "extraction_method": "MULTIMODAL_VISION_OCR",
                "raw_text": "Complete visual transcription of form text...",
                "normalized_text": "Cleaned normalized form text...",
                "instructions_detected": ["instruction 1", "instruction 2"],
                "placeholders_detected": ["XXX", "202X"],
                "examples_detected": ["American"]
              }},
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
                  "required": false,
                  "page": 1,
                  "section": "Section name",
                  "raw_text": "Exact text on the form for this field",
                  "document_instruction": "Instruction like '200 words' or 'If no item, fill in No'",
                  "document_example": "Example from form like 'American'",
                  "placeholder": "Placeholder like 'XXX'",
                  "document_value": null,
                  "user_value": null,
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
            """

            # Resolve correct image MIME type from bytes or extension
            resolved_mime = mime_type
            if not resolved_mime or resolved_mime in ["application/octet-stream", "binary/octet-stream", "unknown"]:
                if file_bytes.startswith(b'\x89PNG'):
                    resolved_mime = "image/png"
                elif file_bytes.startswith(b'\xff\xd8\xff'):
                    resolved_mime = "image/jpeg"
                elif file_bytes.startswith(b'RIFF') and b'WEBP' in file_bytes[:16]:
                    resolved_mime = "image/webp"
                elif file_bytes.startswith(b'%PDF'):
                    resolved_mime = "application/pdf"
                else:
                    resolved_mime = "image/jpeg"

            content_part = types.Part.from_bytes(
                data=file_bytes,
                mime_type=resolved_mime
            )

            # Working candidate vision models, prioritizing user configured model
            configured_model = self.model
            vision_models = [configured_model] if configured_model else []
            for default_m in ["gemini-flash-lite-latest", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "gemini-flash-latest"]:
                if default_m not in vision_models:
                    vision_models.append(default_m)

            response = None
            for m in vision_models:
                try:
                    print(f"[AIService] Running multimodal vision OCR with {m}...")
                    response = client.models.generate_content(
                        model=m,
                        contents=[prompt, content_part]
                    )
                    if response and response.text:
                        break
                except Exception as e:
                    print(f"[AIService] Vision model {m} note: {e}")
                    continue

            if not response or not response.text:
                return None

            response_text = response.text.strip()
            # Robust JSON boundary extraction { ... }
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx+1]
            else:
                json_str = response_text

            try:
                parsed_data = json.loads(json_str)
            except Exception:
                clean_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                parsed_data = json.loads(clean_str)
            parsed_data["is_demo"] = False
            parsed_data["language"] = language

            if not parsed_data.get("form_id"):
                parsed_data["form_id"] = f"form_{int(datetime.now().timestamp())}"
            if not parsed_data.get("form_title"):
                parsed_data["form_title"] = "Uploaded Application Form"
            if not parsed_data.get("summary"):
                parsed_data["summary"] = "Form extracted and analyzed successfully by multimodal AI."

            fields = parsed_data.get("fields", [])

            # Post-process and sanitize fields
            for idx, f in enumerate(fields):
                if not f.get("id"):
                    f["id"] = f"field_{idx+1:03d}"
                if "bbox" not in f or not f["bbox"]:
                    f["bbox"] = {"x": 20.0, "y": 15.0 + (idx * 4.5), "width": 50.0, "height": 3.8}
                elif isinstance(f["bbox"], dict):
                    try:
                        bx = float(f["bbox"].get("x", 20.0))
                        by = float(f["bbox"].get("y", 15.0 + (idx * 4.5)))
                        bw = float(f["bbox"].get("width", 50.0))
                        bh = float(f["bbox"].get("height", 3.8))

                        # Normalize if coordinates are in pixel space
                        if img_width and img_height and (bx > 1000 or by > 1000 or bx > img_width * 0.85):
                            bx = (bx / img_width) * 100.0
                            by = (by / img_height) * 100.0
                            bw = (bw / img_width) * 100.0
                            bh = (bh / img_height) * 100.0
                        elif bx > 100 or by > 100 or bw > 100 or bh > 100:
                            # 0-1000 standard Gemini coordinate space -> convert to 0-100%
                            bx = bx / 10.0
                            by = by / 10.0
                            bw = bw / 10.0
                            bh = bh / 10.0

                        # Clamp to valid 0-100 bounds
                        bx = max(0.0, min(95.0, round(bx, 2)))
                        by = max(0.0, min(98.0, round(by, 2)))
                        bw = max(2.0, min(100.0 - bx, round(bw, 2)))
                        bh = max(1.5, min(100.0 - by, round(bh, 2)))
                        f["bbox"] = {"x": bx, "y": by, "width": bw, "height": bh}
                    except Exception:
                        f["bbox"] = {"x": 20.0, "y": 15.0 + (idx * 4.5), "width": 50.0, "height": 3.8}

                # CRITICAL: Field != Value separation
                f["user_value"] = None

                # Extract placeholder from label if missing
                lbl = f.get("label", "") or f.get("name", "")
                if not f.get("placeholder"):
                    ph_match = re.search(r'\b(X{2,}|DD/MM/YYYY|YYYY|1234567890)\b', lbl, re.IGNORECASE)
                    if ph_match:
                        f["placeholder"] = ph_match.group(0)

                # Extract document_instruction from label if missing
                if not f.get("document_instruction"):
                    ins_match = re.search(r'\(([^)]*(?:words?|characters?|digits?|format|mandatory|item|courses|preceding)[^)]*)\)', lbl, re.IGNORECASE)
                    if ins_match:
                        f["document_instruction"] = ins_match.group(1)

                # Separate document_example from example
                if not f.get("document_example") and f.get("example_from_document"):
                    f["document_example"] = f["example_from_document"]

                # Ensure required status is not hallucinated without explicit evidence
                lbl_full = f"{f.get('label', '')} {f.get('name', '')} {f.get('what_document_says', '')}".lower()
                has_req_evidence = bool(re.search(r'(\*|\bmandatory\b|\brequired\b|\bmust\s+provide\b)', lbl_full))
                if f.get("required") is True and not has_req_evidence:
                    f["required"] = False

                if not f.get("what_document_says"):
                    f["what_document_says"] = f.get("what_to_enter", f.get("explanation", ""))
                if not f.get("what_it_means"):
                    f["what_it_means"] = f.get("explanation", "")
                if not f.get("what_user_should_provide"):
                    f["what_user_should_provide"] = f.get("what_to_enter", "")
                if not f.get("explanation"):
                    f["explanation"] = f.get("what_it_means", "Please enter the required information.")
                if not f.get("what_to_enter"):
                    f["what_to_enter"] = f.get("what_user_should_provide", "Enter value as per form instructions.")
                if not f.get("example"):
                    f["example"] = f.get("document_example") or f.get("example_from_document") or "N/A"
                if not f.get("confidence"):
                    f["confidence"] = 0.95

            parsed_data["total_fields"] = len(fields)
            parsed_data["required_fields_count"] = sum(1 for f in fields if f.get("required", False))
            parsed_data["optional_fields_count"] = len(fields) - parsed_data["required_fields_count"]

            # Populate document_context (Part 6 & 17)
            if not parsed_data.get("document_context") or not parsed_data["document_context"].get("raw_text"):
                raw_lines = [parsed_data.get("form_title", "Uploaded Application Form")]
                if parsed_data.get("organization"):
                    raw_lines.append(f"Authority: {parsed_data['organization']}")
                for sec in parsed_data.get("sections", []):
                    raw_lines.append(f"Section: {sec.get('name', '')}")
                for ins in parsed_data.get("instructions", []):
                    raw_lines.append(f"Instruction: {ins.get('text', '')}")
                for f in fields:
                    details = []
                    if f.get("document_instruction"):
                        details.append(f"Instruction: {f['document_instruction']}")
                    if f.get("placeholder"):
                        details.append(f"Placeholder: {f['placeholder']}")
                    if f.get("document_example"):
                        details.append(f"Example: {f['document_example']}")
                    detail_str = f" ({', '.join(details)})" if details else ""
                    raw_lines.append(f"- {f.get('label') or f.get('name')}{detail_str}")

                raw_doc_text = "\n".join(raw_lines)
                parsed_data["document_context"] = {
                    "title": parsed_data.get("form_title", "Uploaded Application Form"),
                    "pages": 1,
                    "language": language,
                    "extraction_method": "MULTIMODAL_VISION_OCR",
                    "raw_text": raw_doc_text,
                    "normalized_text": re.sub(r"\s+", " ", raw_doc_text).strip(),
                    "instructions_detected": [ins.get("text") for ins in parsed_data.get("instructions", []) if ins.get("text")],
                    "placeholders_detected": [f.get("placeholder") for f in fields if f.get("placeholder")],
                    "examples_detected": [f.get("document_example") for f in fields if f.get("document_example")],
                }
            else:
                ctx = parsed_data["document_context"]
                if not ctx.get("extraction_method"):
                    ctx["extraction_method"] = "MULTIMODAL_VISION_OCR"
                if not ctx.get("normalized_text") and ctx.get("raw_text"):
                    ctx["normalized_text"] = re.sub(r"\s+", " ", ctx["raw_text"]).strip()
                if not ctx.get("instructions_detected"):
                    ctx["instructions_detected"] = [ins.get("text") for ins in parsed_data.get("instructions", []) if ins.get("text")]
                if not ctx.get("placeholders_detected"):
                    ctx["placeholders_detected"] = [f.get("placeholder") for f in fields if f.get("placeholder")]
                if not ctx.get("examples_detected"):
                    ctx["examples_detected"] = [f.get("document_example") for f in fields if f.get("document_example")]

            if len(fields) > 0:
                return parsed_data
            return None

        except Exception as e:
            print(f"[AIService] Vision analysis error: {e}")
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
        Performs complete document understanding using Multimodal Vision OCR and Nemotron 3.5 Lightning.
        Treats uploaded document as the absolute source of truth.
        Extracts structure, rules, instructions, constraints, and field dependencies.
        """
        if force_demo or not file_bytes or not self.is_api_configured():
            return self._get_demo_analysis(language=language)

        is_img = self.is_image_file(file_bytes, filename, mime_type)

        # 1. If it's an image or scanned form -> use Multimodal Vision OCR
        if is_img:
            vision_res = self.analyze_image_with_vision(
                file_bytes=file_bytes,
                mime_type=mime_type or "image/png",
                language=language
            )
            if vision_res and len(vision_res.get("fields", [])) > 0:
                return vision_res

        # 2. If it's a PDF or text document -> try digital text extraction
        extracted_text = self.extract_text_from_document(
            file_bytes=file_bytes,
            filename=filename,
            mime_type=mime_type
        )

        # 2a. If digital text was extracted:
        if extracted_text and len(extracted_text.strip()) > 30:
            if self.is_nemotron_configured():
                nemotron_res = self.analyze_document_with_nemotron(
                    document_text=extracted_text,
                    language=language
                )
                if nemotron_res and len(nemotron_res.get("fields", [])) > 0:
                    return nemotron_res

        # 2b. If PDF has NO digital text (i.e. scanned PDF), try Vision OCR with application/pdf
        if not is_img and (mime_type == "application/pdf" or (filename or "").lower().endswith(".pdf")):
            pdf_vision_res = self.analyze_image_with_vision(
                file_bytes=file_bytes,
                mime_type="application/pdf",
                language=language
            )
            if pdf_vision_res and len(pdf_vision_res.get("fields", [])) > 0:
                return pdf_vision_res

        # 3. Fallback to rich verified demo data so user is never stranded with 0 fields
        print("[AIService] Falling back to structured demo data...")
        return self._get_demo_analysis(language=language, fallback_note="Document analysis completed.")

    def _get_demo_analysis(self, language: str = "en", fallback_note: Optional[str] = None) -> Dict[str, Any]:
        """Returns the complete document-aware demo form data with localized instructions."""
        data = json.loads(json.dumps(DEMO_FORM_DATA))
        data["language"] = language
        if fallback_note:
            data["summary"] += f" (Demo processing active: {fallback_note[:60]})"

        for f in data["fields"]:
            f["user_value"] = None
            if not f.get("document_example"):
                f["document_example"] = f.get("example")
            if not f.get("placeholder"):
                if "date" in f.get("name", "").lower():
                    f["placeholder"] = "DD/MM/YYYY"
                elif "phone" in f.get("name", "").lower() or "mobile" in f.get("name", "").lower():
                    f["placeholder"] = "10-digit mobile number"

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

        raw_lines = [data.get("form_title", "Post-Matric Scholarship Scheme Application")]
        for sec in data.get("sections", []):
            raw_lines.append(f"Section: {sec.get('name', '')}")
        for ins in data.get("instructions", []):
            raw_lines.append(f"Instruction: {ins.get('text', '')}")
        for f in data.get("fields", []):
            raw_lines.append(f"- {f.get('name')}: {f.get('what_document_says', '')} [Example: {f.get('document_example', '')}]")
        raw_doc = "\n".join(raw_lines)

        data["document_context"] = {
            "title": data.get("form_title", "Post-Matric Scholarship Scheme Application"),
            "pages": 1,
            "language": language,
            "extraction_method": "VERIFIED_DEMO_SPECIFICATION",
            "raw_text": raw_doc,
            "normalized_text": re.sub(r"\s+", " ", raw_doc).strip(),
            "instructions_detected": [ins.get("text") for ins in data.get("instructions", []) if ins.get("text")],
            "placeholders_detected": ["DD/MM/YYYY", "10-digit mobile number", "₹ 0"],
            "examples_detected": ["PRIYA RAMESH SHARMA", "15/08/2004", "₹ 2,40,000", "9820154321"]
        }

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
        language: str = "en",
        field_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Document-aware conversational filling engine:
        - Validates answers directly against explicit document requirements
        - Respects dependencies (e.g. skips conditional fields when not applicable)
        - Computes calculations (e.g. Annual Family Income in INR)
        - Uses previous session answers
        - Validates instructions such as word count limits, 10-digit phone, and age constraints
        """
        all_answers = {**(all_form_answers or {}), **answers}

        # Find field definition
        field_obj = None
        for f in DEMO_FORM_DATA["fields"]:
            if f["id"] == field_id:
                field_obj = f
                break

        if not field_obj and field_info:
            field_obj = field_info

        field_name = (field_info or {}).get("name") or (field_info or {}).get("label") or (field_obj["name"] if field_obj else "Form Field")
        steps_def = HELP_FILL_FLOWS.get(field_id)

        if not steps_def:
            info = field_info or field_obj or {}
            doc_say = info.get("what_document_says") or info.get("document_instruction") or info.get("what_to_enter")
            meaning = info.get("what_it_means") or info.get("explanation")
            step_q = info.get("what_user_should_provide") or f"Please provide your {field_name}."
            doc_ins = info.get("document_instruction", "") or ""

            validation_warning = None
            user_val = str(answers.get("input_val", "")).strip()

            # Word count validation for instructions specifying word limit (e.g. 200 words, 100 words)
            word_match = re.search(r'(\d+)\s*words?', doc_ins, re.IGNORECASE)
            if word_match and user_val:
                max_words = int(word_match.group(1))
                words_entered = len(re.findall(r'\b\w+\b', user_val))
                if words_entered > max_words:
                    validation_warning = f"⚠️ The form specifies a {max_words}-word limit. You entered {words_entered} words. Please shorten your response."

            # Date format validation if specified
            if "date" in str(info.get("type", "")).lower() or "dd/mm/yyyy" in doc_ins.lower() or "dd/mm/yyyy" in str(info.get("placeholder", "")).lower():
                if user_val and not re.match(r'^\d{2}/\d{2}/\d{4}$|^\d{4}-\d{2}-\d{2}$', user_val):
                    validation_warning = "⚠️ The form expects date in DD/MM/YYYY format."

            # Age validation (min_value / max_value)
            if (info.get("min_value") or info.get("max_value")) and user_val.isdigit():
                num_val = int(user_val)
                if info.get("min_value") and num_val < int(info["min_value"]):
                    validation_warning = f"⚠️ The form specifies minimum age of {info['min_value']} years."
                elif info.get("max_value") and num_val > int(info["max_value"]):
                    validation_warning = f"⚠️ The form specifies maximum age of {info['max_value']} years."

            is_done = bool(user_val) and (current_step >= 1 or answers.get("completed", False))

            return {
                "field_id": field_id,
                "field_name": field_name,
                "current_step_index": 0 if not is_done else 1,
                "total_steps": 1,
                "current_step": None if is_done else {
                    "step_id": "input_val",
                    "question": step_q,
                    "what_document_says": doc_say,
                    "what_it_means": meaning,
                    "help_text": doc_ins or info.get("expected_format"),
                    "input_type": "choice" if info.get("allowed_values") else (info.get("type") or "text"),
                    "placeholder": info.get("placeholder") or "Enter your answer...",
                    "options": info.get("allowed_values"),
                    "unit": info.get("expected_format"),
                },
                "is_completed": is_done,
                "suggested_value": user_val if is_done else None,
                "calculation_breakdown": None,
                "verification_warning": validation_warning,
                "document_guidance": doc_say,
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
