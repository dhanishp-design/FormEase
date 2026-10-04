from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x: float = Field(..., description="X coordinate percentage (0-100)")
    y: float = Field(..., description="Y coordinate percentage (0-100)")
    width: float = Field(..., description="Width percentage (0-100)")
    height: float = Field(..., description="Height percentage (0-100)")

class FormField(BaseModel):
    id: str
    name: str
    type: str  # text, number, currency, date, phone, email, address, checkbox, radio, dropdown, signature, unknown
    required: bool
    page: int = 1
    section: str
    explanation: str
    what_to_enter: str
    example: str
    confidence: float
    sensitive: bool = False
    bbox: Optional[BoundingBox] = None
    translations: Optional[Dict[str, Dict[str, str]]] = None  # {"hi": {"explanation": ..., "what_to_enter": ...}, "mr": {...}}

class FormAnalysisResponse(BaseModel):
    form_id: str
    form_title: str
    summary: str
    total_fields: int
    required_fields_count: int
    optional_fields_count: int
    overall_confidence: float
    language: str = "en"
    is_demo: bool = False
    document_preview_url: Optional[str] = None
    fields: List[FormField]

class FieldExplainRequest(BaseModel):
    field_id: str
    form_id: Optional[str] = None
    language: str = "en"

class FieldExplainResponse(BaseModel):
    field_id: str
    name: str
    explanation: str
    what_to_enter: str
    example: str
    required: bool
    confidence: float
    sensitive: bool
    language: str

class HelpFillStep(BaseModel):
    step_id: str
    question: str
    help_text: Optional[str] = None
    input_type: str  # number, text, date, choice, currency, boolean
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None
    unit: Optional[str] = None

class HelpFillRequest(BaseModel):
    field_id: str
    current_step: int = 0
    answers: Dict[str, Any] = Field(default_factory=dict)
    language: str = "en"

class HelpFillResponse(BaseModel):
    field_id: str
    field_name: str
    current_step_index: int
    total_steps: int
    current_step: Optional[HelpFillStep] = None
    is_completed: bool = False
    calculation_breakdown: Optional[str] = None
    suggested_value: Optional[str] = None
    verification_warning: Optional[str] = None
    language: str = "en"

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    form_title: Optional[str] = None
    selected_field_id: Optional[str] = None
    language: str = "en"
    history: List[ChatMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str
    suggested_questions: List[str] = Field(default_factory=list)
