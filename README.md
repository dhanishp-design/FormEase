# FormEase

> **Understand Any Form. Fill It With Confidence.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-Multimodal-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev)

---

## 1. Problem

Official application forms—scholarships, college admissions, welfare schemes, domicile declarations, and banking authorizations—are packed with dense legalese, ambiguous terms, and confusing requirements. 

Every year, millions of students and citizens face rejection, delays, or severe anxiety simply because they misinterpret fields such as *"Annual Family Income"*, *"Domicile State"*, *"Non-Creamy Layer"*, or *"IFSC Code"*. 

Existing tools either offer generic chatbots that lack document spatial context or provide basic PDF viewers that do not explain what inputs actually mean.

---

## 2. Solution

**FormEase** is an AI-powered form understanding assistant. Users can upload any PDF or image form (scholarship, government, admissions, or banking). FormEase analyzes the document using multimodal AI, extracts all structured fields with coordinates, and transforms bureaucratic language into clear, human-readable explanations.

### The Core Experience
```text
UPLOAD FORM
     ↓
AI ANALYZES FORM
     ↓
DETECT FIELDS
     ↓
SHOW FORM + FIELD INFORMATION
     ↓
SELECT / HIGHLIGHT A FIELD
     ↓
AI EXPLAINS FIELD
     ↓
HELP ME FILL THIS
     ↓
AI ASKS SIMPLE QUESTIONS
     ↓
GENERATES SUGGESTED VALUE
     ↓
USER REVIEWS AND CONFIRMS
```

---

## 3. Killer Features

### 💡 Highlight Any Field → Understand It
The document preview is rendered on the left and the AI Field Assistant on the right. When the user clicks any detected field on the document or in the sidebar:
- FormEase immediately highlights the entry with an interactive glowing bounding box.
- Displays **What does this mean?** in plain language.
- Displays **What should you enter?** with concrete instructions.
- Provides realistic **Examples** (e.g. `₹4,80,000`).
- Shows whether the field is **Required** or **Optional**, along with the AI Confidence level.
- Alerts the user if the field contains sensitive banking or identity data (Aadhaar, PAN, Bank Details).

### ✨ "Help Me Fill This" Interactive Calculator
Instead of leaving the user to do complex mental math or look up equations, clicking **Help Me Fill This** opens a conversational, step-by-step guidance interface:
- **Annual Family Income**: Asks father's monthly income (e.g. `₹30,000`), mother's monthly income (e.g. `₹10,000`), calculates `₹30,000 × 12 = ₹3,60,000` + `₹10,000 × 12 = ₹1,20,000` = `₹4,80,000`, displays the formula breakdown, and provides a **Use This Value** button with caution advisories.
- **Date of Birth**: Formats and validates `DD/MM/YYYY`.
- **Mobile Number**: Validates 10-digit format and Aadhaar-DBT linking prerequisites.
- **Domicile & Category**: Explains legal eligibility certificates without making assumptions.

### 🌐 Multilingual Accessibility (English, हिन्दी, मराठी)
Switch languages in real-time. FormEase adapts field explanations, instructions, and conversational guidance into **Hindi** and **Marathi**, preserving official nomenclature while simplifying comprehension.

### 💬 Document-Grounded AI Chat
Ask natural questions with full document context:
- *"What does domicile mean?"*
- *"What is an IFSC code and where do I find it?"*
- *"Is income certificate mandatory for this form?"*
- *"What is the difference between permanent and current address?"*

### 📋 Pre-Submission Form Review & Progress Tracker
- Real-time progress bar (e.g., `8 / 12 fields reviewed • 67%`).
- Pre-submission audit checking required fields, date formats, email syntax, and mobile length.
- Never fabricates legal certainty; clearly marks entries as *"Ready for your review"* with human verification safeguards.

---

## 4. Architecture & Tech Stack

```text
┌────────────────────────────────────────────────────────┐
│                   FormEase Frontend                    │
│      React 19 + TypeScript + Vite + Tailwind CSS       │
│  (DocumentViewer + FieldAssistant + HelpFill + Chat)   │
└───────────────────────────┬────────────────────────────┘
                            │ REST JSON & Multipart Uploads
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FormEase Backend                     │
│                  FastAPI (Python 3.14)                 │
│    (CORS + Pydantic v2 Validation + Route Handlers)    │
└─────────────┬───────────────────────────┬──────────────┘
              │                           │
              ▼                           ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│ Multimodal AI Service     │ │ Resilient Mock Engine    │
│ (Google Gemini 2.0 Flash) │ │ (Pre-calculated recipes, │
│ Multi-field extraction,   │ │  coordinates & offline   │
│ spatial bounding boxes    │ │  demo mode)              │
└───────────────────────────┘ └──────────────────────────┘
```

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide React Icons.
- **Backend**: FastAPI, Uvicorn, Python-Multipart, Pydantic v2.
- **Multimodal AI**: Google Gemini (`gemini-2.0-flash`, `gemini-1.5-flash`), with automated fallback to verified demo data.

---

## 5. Getting Started & Local Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### Clone & Setup

```bash
git clone <repo-url>
cd FormEase
```

### Backend Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python app.py
```
Backend will start on `http://127.0.0.1:8000` (Interactive API docs at `http://127.0.0.1:8000/docs`).

### Frontend Setup

In a new terminal:

```bash
# Navigate to frontend or run from root
npm install
npm run dev
```
Frontend will be available at `http://localhost:5173`.

---

## 6. Environment Variables

Create `.env` based on `.env.example`:

```bash
cp .env.example .env
```

```env
# Optional: Set your Gemini API key for live multimodal processing
AI_API_KEY=your_gemini_api_key_here
AI_MODEL=gemini-2.0-flash

# Server settings
HOST=127.0.0.1
PORT=8000
```
> **Note:** If no `AI_API_KEY` is provided, FormEase seamlessly runs in **Demo Mode**, providing the full interactive experience with 12 realistic fields and multi-step calculations.

---

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and AI configuration check |
| `POST` | `/api/analyze` | Multipart upload for PDF/Images; returns structured fields & coordinates |
| `POST` | `/api/explain` | Returns in-depth field explanations in English, Hindi, or Marathi |
| `POST` | `/api/help-fill` | Manages multi-step guided question trees and automated calculations |
| `POST` | `/api/chat` | Context-aware chat grounded in uploaded document structure |

---

## 8. Hackathon 90-Second Demo Script

Follow this flow for presentations:

1. **Scene 1 — Problem (0:00 - 0:15)**: Open FormEase. Say: *"Forms are everywhere, but understanding them isn't. FormEase is the AI assistant that explains any form in human language."*
2. **Scene 2 — Upload / Demo (0:15 - 0:30)**: Click **Try Demo Form**. Watch the 4-stage analysis progress: *"Reading document → Detecting fields → Understanding instructions → Preparing explanations"*.
3. **Scene 3 — Workspace (0:30 - 0:45)**: Show the split screen: form on the left with interactive bounding boxes, assistant on the right.
4. **Scene 4 — Killer Feature (0:45 - 1:00)**: Click **Annual Family Income**. Show the highlighted box, plain language explanation, and example `₹4,80,000`.
5. **Scene 5 — Help Me Fill This (1:00 - 1:15)**: Click **Help Me Fill This**.
   - Father's monthly income: `₹30,000`
   - Mother has income? `Yes`
   - Mother's monthly income: `₹10,000`
   - Watch FormEase calculate `₹30,000 × 12` + `₹10,000 × 12` = **₹4,80,000**.
   - Click **Use This Value**.
6. **Scene 6 — Multilingual (1:15 - 1:25)**: Switch language from **EN** to **मराठी** or **हिन्दी**. Watch the explanation and assistance change instantly.
7. **Scene 7 — Review & Wrap (1:25 - 1:30)**: Click **Review Form** to show pre-submission checklist. Conclude: *"FormEase — No one should be confused by a form again."*

---

## 9. Privacy & Security Safeguards

- **Ephemeral Processing**: Documents are analyzed in memory and not stored permanently.
- **Sensitive Data Detection**: FormEase flags bank account, Aadhaar, and identity entries with cautionary review warnings.
- **No Hallucinated Legal Rules**: FormEase clearly distinguishes between linguistic clarification and official authority, requiring human confirmation before any official submission.

---

## 10. Future Roadmap

- [ ] Automated PDF Form Fill Export (overlaying verified entries directly onto blank PDF fields).
- [ ] Voice-assisted filling for users with low literacy or visual impairments.
- [ ] Regional dialect expansion (Tamil, Telugu, Bengali, Gujarati).
- [ ] Educational institution verification portal for scholarship counselors.

---

## 11. Testing

To run the backend test suite:

```bash
.venv\Scripts\python -m unittest backend/test_api.py
```

All 7 test cases validate file type restrictions, demo mode extraction, multilingual translations, income math calculations, and chat responses.

---

## 12. License & Credits

Developed with ❤️ for accessibility and confidence by the FormEase Team.
Distributed under the Apache-2.0 License.
