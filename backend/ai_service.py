import os
import json
import base64
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from backend.demo_data import DEMO_FORM_DATA, HELP_FILL_FLOWS
from backend.models import FormField, BoundingBox

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash").strip()

class AIService:
    def __init__(self):
        self.api_key = AI_API_KEY
        self.model = AI_MODEL

    def is_api_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def analyze_document(
        self,
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        language: str = "en",
        force_demo: bool = False
    ) -> Dict[str, Any]:
        """
        Analyzes a document (PDF or Image) using multimodal AI.
        Falls back cleanly to demo data or intelligent mock if API is not configured or fails.
        """
        if force_demo or not file_bytes or not self.is_api_configured():
            return self._get_demo_analysis(language=language)

        try:
            prompt = f"""
            You are FormEase, an expert AI document & form understanding assistant.
            Analyze this uploaded form image or document.
            Return ONLY a valid JSON object with the following schema, and no extra text or markdown ticks:
            {{
              "form_title": "Identified Official Form Title",
              "summary": "2-3 sentences explaining the purpose of this form and who needs to fill it.",
              "total_fields": <integer count>,
              "required_fields_count": <integer count>,
              "optional_fields_count": <integer count>,
              "overall_confidence": 0.94,
              "fields": [
                {{
                  "id": "field_001",
                  "name": "Field Name as printed on form",
                  "type": "text | number | currency | date | phone | email | address | checkbox | radio | dropdown | signature | unknown",
                  "required": true,
                  "page": 1,
                  "section": "Section name if applicable",
                  "explanation": "Clear, simple plain language explanation of what this field means.",
                  "what_to_enter": "Direct instruction on what specific information the applicant should enter.",
                  "example": "Realistic example entry",
                  "confidence": 0.95,
                  "sensitive": false,
                  "bbox": {{ "x": 10.0, "y": 20.0, "width": 40.0, "height": 4.0 }}
                }}
              ]
            }}
            Identify up to 10-15 most prominent fields. For sensitive fields (Aadhaar, PAN, Bank Details, Passwords), set sensitive: true.
            Never hallucinate legal criteria. Explain fields in plain, friendly language.
            """

            if self.api_key.startswith("sk-or-"):
                import openai
                client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
                
                if file_bytes:
                    base64_image = base64.b64encode(file_bytes).decode('utf-8')
                    messages[0]["content"].append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type or 'image/jpeg'};base64,{base64_image}"
                        }
                    })

                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                response_text = response.choices[0].message.content.strip()
            else:
                # Attempt live multimodal Gemini call
                from google import genai
                client = genai.Client(api_key=self.api_key)
                
                # Pass document to Gemini
                content_part = {
                    "mime_type": mime_type or "image/jpeg",
                    "data": file_bytes
                }
                
                response = client.models.generate_content(
                    model=self.model,
                    contents=[prompt, content_part]
                )
                response_text = response.text.strip()
            # Clean possible markdown block
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            parsed_data = json.loads(response_text.strip())
            parsed_data["is_demo"] = False
            parsed_data["language"] = language
            
            # Ensure bbox and sensitive defaults
            for idx, f in enumerate(parsed_data.get("fields", [])):
                if not f.get("id"):
                    f["id"] = f"field_{idx+1:03d}"
                if "bbox" not in f or not f["bbox"]:
                    f["bbox"] = {"x": 20.0, "y": 15.0 + (idx * 5.5), "width": 45.0, "height": 4.0}
            
            return parsed_data

        except Exception as e:
            print(f"[AIService] AI Analysis error or fallback: {e}")
            return self._get_demo_analysis(language=language, fallback_note=str(e))

    def _get_demo_analysis(self, language: str = "en", fallback_note: Optional[str] = None) -> Dict[str, Any]:
        """Returns the high-fidelity demo scholarship form with localized explanations."""
        data = json.loads(json.dumps(DEMO_FORM_DATA))
        data["language"] = language
        if fallback_note:
            data["summary"] += f" (Demo processing active: {fallback_note[:60]})"

        # Apply localized translations if language is hi or mr
        if language in ("hi", "mr"):
            for field in data["fields"]:
                trans = field.get("translations", {}).get(language)
                if trans:
                    field["explanation"] = trans.get("explanation", field["explanation"])
                    field["what_to_enter"] = trans.get("what_to_enter", field["what_to_enter"])
                    field["example"] = trans.get("example", field["example"])

        return data

    def explain_field(self, field_id: str, language: str = "en") -> Dict[str, Any]:
        """Provides an in-depth explanation of a specific field in the selected language."""
        for field in DEMO_FORM_DATA["fields"]:
            if field["id"] == field_id:
                explanation = field["explanation"]
                what_to_enter = field["what_to_enter"]
                example = field["example"]

                if language in ("hi", "mr") and "translations" in field:
                    trans = field["translations"].get(language, {})
                    explanation = trans.get("explanation", explanation)
                    what_to_enter = trans.get("what_to_enter", what_to_enter)
                    example = trans.get("example", example)

                return {
                    "field_id": field["id"],
                    "name": field["name"],
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
            "explanation": "Please review the form instructions for this entry.",
            "what_to_enter": "Enter the required information.",
            "example": "N/A",
            "required": False,
            "confidence": 0.8,
            "sensitive": False,
            "language": language
        }

    def process_help_fill(self, field_id: str, current_step: int, answers: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Manages the dynamic multi-step guided filling experience.
        Special calculations for Annual Family Income (Father + Mother + Other) and formats.
        """
        # Find field name
        field_name = "Form Field"
        for f in DEMO_FORM_DATA["fields"]:
            if f["id"] == field_id:
                field_name = f["name"]
                break

        steps_def = HELP_FILL_FLOWS.get(field_id)
        if not steps_def:
            # Generic smart fill flow
            return {
                "field_id": field_id,
                "field_name": field_name,
                "current_step_index": 0,
                "total_steps": 1,
                "is_completed": True,
                "suggested_value": answers.get("input_val", ""),
                "calculation_breakdown": None,
                "verification_warning": "Please verify this value against your official documents before submission.",
                "language": language
            }

        total_steps = len(steps_def)

        # Handle Annual Family Income calculation when reaching the end
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
                # Indian currency formatting
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
                f"• Father's Income: {fmt_inr(f_m)}/month × 12 = {fmt_inr(f_annual)}/year",
            ]
            if answers.get("mother_has_income") == "Yes" and m_m > 0:
                breakdown_lines.append(f"• Mother's Income: {fmt_inr(m_m)}/month × 12 = {fmt_inr(m_annual)}/year")
            if other_y > 0:
                breakdown_lines.append(f"• Other Income: {fmt_inr(other_y)}/year")
            breakdown_lines.append(f"• Estimated Total Annual Family Income = {suggested}")

            warning_text = {
                "en": "⚠ Please verify this amount against your official Income Certificate issued by the Tehsildar/Revenue Authority before submitting.",
                "hi": "⚠ कृपया सबमिट करने से पहले तहसीलदार/राजस्व अधिकारी द्वारा जारी अपने आधिकारिक आय प्रमाण पत्र से इस राशि का मिलान अवश्य करें।",
                "mr": "⚠ कृपया अर्ज सादर करण्यापूर्वी तहसीलदार किंवा सक्षम प्राधिकरणाने दिलेल्या अधिकृत उत्पन्न प्रमाणपत्राशी ही रक्कम पडताळून पहा."
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
                "language": language
            }

        # Check if flow is completed for other fields
        if current_step >= total_steps:
            # Gather suggested value
            first_ans = next(iter(answers.values()), "") if answers else ""
            suggested = str(first_ans)
            
            # Format date if field_002
            if field_id == "field_002" and suggested:
                # format to DD/MM/YYYY if YYYY-MM-DD
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
                "verification_warning": "Please ensure this matches your official records.",
                "language": language
            }

        # Render current step
        step_raw = steps_def[current_step]
        
        # Check conditional
        if "conditional_on" in step_raw:
            cond = step_raw["conditional_on"]
            cond_val = answers.get(cond["step_id"])
            if cond_val != cond["value"]:
                # Skip this step and advance
                return self.process_help_fill(field_id, current_step + 1, answers, language)

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
                "help_text": help_text,
                "input_type": step_raw.get("input_type", "text"),
                "placeholder": step_raw.get("placeholder", ""),
                "options": step_raw.get("options", []),
                "unit": step_raw.get("unit", "")
            },
            "is_completed": False,
            "calculation_breakdown": None,
            "suggested_value": None,
            "verification_warning": None,
            "language": language
        }

    def chat_about_form(
        self,
        message: str,
        form_title: Optional[str] = None,
        selected_field_id: Optional[str] = None,
        language: str = "en",
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Answers form-related questions grounded in the uploaded form context.
        Provides accurate explanations without hallucinating legal requirements.
        """
        msg_lower = message.lower()

        # Multilingual response presets and contextual patterns
        if "domicile" in msg_lower or "अधिवास" in msg_lower:
            replies = {
                "en": "Domicile refers to the state or place where you are legally recognized as a permanent resident. For this scholarship, you will need a valid Domicile Certificate issued by a Tehsildar or Executive Magistrate to prove you reside in the state offering the scheme.",
                "hi": "अधिवास (Domicile) उस राज्य को दर्शाता है जहां आप कानूनी रूप से स्थायी निवासी हैं। इस छात्रवृत्ति के लिए, यह प्रमाणित करने के लिए कि आप राज्य के स्थायी निवासी हैं, तहसीलदार या सक्षम अधिकारी द्वारा जारी डोमिसाइल प्रमाणपत्र आवश्यक होता है।",
                "mr": "अधिवास (Domicile) म्हणजे तुम्ही ज्या राज्याचे कायदेशीर कायमस्वरूपी रहिवासी आहात ते राज्य. या शिष्यवृत्तीसाठी तुम्ही संबंधित राज्याचे रहिवासी असल्याचे सिद्ध करण्यासाठी तहसीलदार किंवा अधिकृत अधिकाऱ्याने दिलेले अधिवास प्रमाणपत्र आवश्यक असते."
            }
            return {
                "reply": replies.get(language, replies["en"]),
                "suggested_questions": [
                    "What documents are needed for domicile proof?",
                    "Is income certificate mandatory?",
                    "Can I edit a field after submitting?"
                ]
            }

        if "ifsc" in msg_lower or "आईएफएससी" in msg_lower:
            replies = {
                "en": "IFSC (Indian Financial System Code) is an 11-character alphanumeric code that uniquely identifies your specific bank branch. You can find it printed on the first page of your bank passbook or on a cheque leaf. The 5th character is always '0'.",
                "hi": "IFSC (भारतीय वित्तीय प्रणाली कोड) 11 वर्णों का एक कोड है जो आपकी बैंक शाखा की विशिष्ट पहचान करता है। यह आपकी बैंक पासबुक के पहले पन्ने या चेक बुक पर लिखा होता है। इसका 5वां अक्षर हमेशा '0' होता है।",
                "mr": "IFSC (इंडियन फायनान्शियल सिस्टीम कोड) हा ११ अक्षरी कोड असतो जो तुमच्या बँकेची विशिष्ट शाखा ओळखतो. हा कोड तुमच्या बँक पासबुकच्या पहिल्या पानावर किंवा चेकवर छापलेला असतो. याचा ५वा अंक नेहमी '०' (शून्य) असतो."
            }
            return {
                "reply": replies.get(language, replies["en"]),
                "suggested_questions": [
                    "Does my bank account need to be linked with Aadhaar?",
                    "What if my bank merged?",
                    "Can I use a parent's bank account?"
                ]
            }

        if "mandatory" in msg_lower or "required" in msg_lower or "अनिवार्य" in msg_lower or "आवश्यक" in msg_lower:
            replies = {
                "en": "In this form, 9 out of 12 fields are mandatory (marked with a red asterisk *), including Full Name, Date of Birth, Annual Family Income, Domicile, Mobile Number, Email, and Bank Details. Father's Occupation is optional.",
                "hi": "इस फॉर्म में 12 में से 9 फ़ील्ड अनिवार्य (लाल स्टार * से चिह्नित) हैं, जिनमें पूरा नाम, जन्म तिथि, पारिवारिक आय, डोमिसाइल, मोबाइल और बैंक विवरण शामिल हैं। पिता का व्यवसाय ऐच्छिक है।",
                "mr": "या अर्जामध्ये १२ पैकी ९ रकाने अनिवार्य आहेत (लाल तारांकित *), ज्यामध्ये पूर्ण नाव, जन्मतारीख, कौटुंबिक उत्पन्न, अधिवास, मोबाईल नंबर आणि बँक खात्याचा तपशील समाविष्ट आहे. वडिलांचा व्यवसाय ऐच्छिक आहे."
            }
            return {
                "reply": replies.get(language, replies["en"]),
                "suggested_questions": [
                    "How to calculate Annual Family Income?",
                    "What happens if I make a mistake?",
                    "Which category documents are required?"
                ]
            }

        if "address" in msg_lower or "permanent" in msg_lower or "current" in msg_lower or "पत्ता" in msg_lower:
            replies = {
                "en": "Permanent Address is your fixed parental or native home address shown on your identity records (Aadhaar/Voter ID). Current/Correspondence Address is where you currently reside (such as a college hostel or rented flat) for receiving physical mail.",
                "hi": "स्थायी पता (Permanent Address) वह मूल पता है जहां आपका परिवार स्थायी रूप से रहता है (आधार कार्ड वाला पता)। वर्तमान पता (Current Address) वह है जहां आप वर्तमान में पढ़ाई या काम के लिए रह रहे हैं।",
                "mr": "कायमचा पत्ता (Permanent Address) म्हणजे तुमचे मूळ गावाकडील किंवा कुटुंबाचे अधिकृत घर (आधार कार्डवरील पत्ता). तर चालू पत्ता (Current Address) म्हणजे तुम्ही सध्या शिक्षण किंवा नोकरीसाठी राहत असलेले ठिकाण (उदा. वसतिगृह किंवा भाड्याची खोली)."
            }
            return {
                "reply": replies.get(language, replies["en"]),
                "suggested_questions": [
                    "What if my current address is different from Aadhaar?",
                    "What is a PIN code?",
                    "Help me fill my address"
                ]
            }

        # If live AI is available, ask Gemini with grounding
        if self.is_api_configured():
            try:
                system_context = f"""
                You are FormEase Assistant, an empathetic, clear, and trustworthy form helper.
                The user is filling out: {form_title or 'an official application form'}.
                Currently selected field: {selected_field_id or 'None'}.
                User language: {language} (en=English, hi=Hindi, mr=Marathi).
                Rules:
                - Explain complicated terminology in simple everyday language.
                - NEVER hallucinate government rules, legal advice, or official deadlines.
                - If not sure, remind the user to check the original form guidelines.
                - Keep answers concise (2-4 sentences).
                - Respond strictly in the requested language: {language}.
                """
                
                if self.api_key.startswith("sk-or-"):
                    import openai
                    client = openai.OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.api_key,
                    )
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_context},
                            {"role": "user", "content": f"User Question: {message}"}
                        ]
                    )
                    reply_text = response.choices[0].message.content.strip()
                else:
                    from google import genai
                    client = genai.Client(api_key=self.api_key)
                    response = client.models.generate_content(
                        model=self.model,
                        contents=[system_context, f"User Question: {message}"]
                    )
                    reply_text = response.text.strip()
                    
                return {
                    "reply": reply_text,
                    "suggested_questions": [
                        "What documents are needed?",
                        "Is this field mandatory?",
                        "Help me fill this field"
                    ]
                }
            except Exception as e:
                print(f"[AIService] Chat generation error: {e}")

        # Default fallback answer
        replies = {
            "en": f"Regarding your question about '{message}': FormEase recommends verifying the official guidelines printed on your form instructions. If you need step-by-step guidance on any specific field, select it on the document preview to see what to enter or click 'Help Me Fill This'.",
            "hi": f"आपके प्रश्न के संदर्भ में: FormEase सलाह देता है कि आप फॉर्म के साथ दिए गए आधिकारिक निर्देशों की जांच करें। किसी विशेष फ़ील्ड को समझने के लिए उस पर क्लिक करें।",
            "mr": f"तुमच्या प्रश्नाबाबत: अर्जाच्या सूचना पत्रिकेतील अधिकृत नियम तपासा. कोणत्याही विशिष्ट रकान्याची मदत हवी असल्यास त्यावर क्लिक करा किंवा 'Help Me Fill This' चा वापर करा."
        }
        return {
            "reply": replies.get(language, replies["en"]),
            "suggested_questions": [
                "What does Domicile mean?",
                "What is an IFSC code?",
                "How to calculate Annual Family Income?"
            ]
        }

ai_service = AIService()
