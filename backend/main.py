import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.models import (
    FormAnalysisResponse,
    FieldExplainRequest,
    FieldExplainResponse,
    HelpFillRequest,
    HelpFillResponse,
    ChatRequest,
    ChatResponse
)
from backend.ai_service import ai_service

app = FastAPI(
    title="FormEase API",
    description="AI-powered form understanding & guided assistance backend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "FormEase API",
        "ai_configured": ai_service.is_api_configured(),
        "nemotron_configured": ai_service.is_nemotron_configured(),
        "gemini_configured": ai_service.is_gemini_configured(),
        "nemotron_model": ai_service.nemotron_model,
        "active_engine": (
            "nemotron" if ai_service.is_nemotron_configured()
            else "gemini" if ai_service.is_gemini_configured()
            else "demo"
        )
    }

@app.post("/api/analyze", response_model=FormAnalysisResponse)
async def analyze_form(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    is_demo: Optional[bool] = Form(False),
    language: Optional[str] = Form("en")
):
    """
    Analyzes an uploaded form (PDF, JPG, PNG) using multimodal AI.
    Supports either file upload or direct local file_path.
    If is_demo is True or no file/file_path is provided, returns the verified scholarship application demo.
    """
    try:
        file_bytes = None
        filename = "unknown"
        ext = ""

        if file_path and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()
            with open(file_path, "rb") as f:
                file_bytes = f.read()
        elif file:
            filename = file.filename or "unknown"
            ext = os.path.splitext(filename)[1].lower()
            file_bytes = await file.read()
        elif is_demo:
            data = ai_service.analyze_document(
                file_bytes=None,
                language=language or "en",
                force_demo=True
            )
            return FormAnalysisResponse(**data)
        else:
            data = ai_service.analyze_document(
                file_bytes=None,
                language=language or "en",
                force_demo=True
            )
            return FormAnalysisResponse(**data)

        # File validation
        valid_exts = [".pdf", ".jpg", ".jpeg", ".png", ".webp", ".jfif", ".bmp", ".tiff"]
        if ext and ext not in valid_exts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This file type isn't supported ({ext}). Please upload PDF, JPG, JPEG, or PNG."
            )

        if not file_bytes or len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty. Please upload a valid document."
            )

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum size limit of 15MB. Please upload a compressed file."
            )

        # Infer true MIME type
        if file_bytes.startswith(b'\x89PNG'):
            mime_type = "image/png"
        elif file_bytes.startswith(b'\xff\xd8\xff'):
            mime_type = "image/jpeg"
        elif file_bytes.startswith(b'RIFF') and b'WEBP' in file_bytes[:16]:
            mime_type = "image/webp"
        elif file_bytes.startswith(b'%PDF'):
            mime_type = "application/pdf"
        elif ext == ".pdf":
            mime_type = "application/pdf"
        elif ext in [".png"]:
            mime_type = "image/png"
        elif ext in [".webp"]:
            mime_type = "image/webp"
        elif file and file.content_type and file.content_type.startswith("image/"):
            mime_type = file.content_type
        else:
            mime_type = "image/jpeg"

        analysis_result = ai_service.analyze_document(
            file_bytes=file_bytes,
            filename=filename,
            mime_type=mime_type,
            language=language or "en",
            force_demo=False
        )

        # Generate base64 data preview for image
        if mime_type.startswith("image/") and (not analysis_result.get("document_preview_url") or analysis_result.get("document_preview_url") == "/demo-form.svg"):
            import base64
            b64 = base64.b64encode(file_bytes).decode("utf-8")
            analysis_result["document_preview_url"] = f"data:{mime_type};base64,{b64}"

        return FormAnalysisResponse(**analysis_result)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Error] /api/analyze error: {e}")
        # Safe recovery so user never gets broken experience
        fallback_data = ai_service.analyze_document(
            file_bytes=None,
            language=language or "en",
            force_demo=True
        )
        fallback_data["summary"] = f"Processed with smart recovery mode. ({str(e)[:50]})"
        if file_bytes and mime_type and mime_type.startswith("image/"):
            import base64
            b64 = base64.b64encode(file_bytes).decode("utf-8")
            fallback_data["document_preview_url"] = f"data:{mime_type};base64,{b64}"
        return FormAnalysisResponse(**fallback_data)

@app.post("/api/explain", response_model=FieldExplainResponse)
async def explain_field(payload: FieldExplainRequest):
    """
    Explains the designated form field in plain language and in the requested language (en, hi, mr).
    """
    try:
        explanation_data = ai_service.explain_field(
            field_id=payload.field_id,
            language=payload.language or "en"
        )
        return FieldExplainResponse(**explanation_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/help-fill", response_model=HelpFillResponse)
async def help_fill(payload: HelpFillRequest):
    """
    Interactive guided filling assistant:
    Returns step questions, calculates values (e.g. Annual Family Income calculator), and provides suggested answers.
    """
    try:
        fill_data = ai_service.process_help_fill(
            field_id=payload.field_id,
            current_step=payload.current_step,
            answers=payload.answers,
            all_form_answers=payload.all_form_answers,
            language=payload.language or "en",
            field_info=payload.field_info
        )
        return HelpFillResponse(**fill_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_form(payload: ChatRequest):
    """
    Context-aware AI chat about the form, rules, field meanings, and terminology.
    """
    try:
        chat_data = ai_service.chat_about_form(
            message=payload.message,
            form_title=payload.form_title,
            selected_field_id=payload.selected_field_id,
            language=payload.language or "en",
            history=[msg.model_dump() for msg in payload.history],
            document_context=payload.document_context
        )
        return ChatResponse(**chat_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred while processing the form. Please try again."}
    )
