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
    label: Optional[str] = None
    type: str  # text, number, currency, date, phone, email, address, checkbox, radio, dropdown, signature, unknown
    required: bool
    page: int = 1
    section: str
    
    # Document Source-of-Truth enhancements
    what_document_says: Optional[str] = None
    what_it_means: Optional[str] = None
    what_user_should_provide: Optional[str] = None
    expected_format: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    example_from_document: Optional[str] = None
    validation_rules: Optional[List[str]] = None
    dependencies: Optional[List[Dict[str, Any]]] = None
    related_fields: Optional[List[str]] = None

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
    purpose: Optional[str] = None
    organization: Optional[str] = None
    summary: str
    total_fields: int
    required_fields_count: int
    optional_fields_count: int
    overall_confidence: float
    language: str = "en"
    is_demo: bool = False
    document_preview_url: Optional[str] = None
    instructions: Optional[List[Dict[str, Any]]] = None
    sections: Optional[List[Dict[str, Any]]] = None
    fields: List[FormField]

class FieldExplainRequest(BaseModel):
    field_id: str
    form_id: Optional[str] = None
    language: str = "en"

class FieldExplainResponse(BaseModel):
    field_id: str
    name: str
    what_document_says: Optional[str] = None
    what_it_means: Optional[str] = None
    what_user_should_provide: Optional[str] = None
    expected_format: Optional[str] = None
    allowed_values: Optional[List[str]] = None
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
    what_document_says: Optional[str] = None
    what_it_means: Optional[str] = None
    help_text: Optional[str] = None
    input_type: str  # number, text, date, choice, currency, boolean
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None
    unit: Optional[str] = None
    validation_rule: Optional[str] = None

class HelpFillRequest(BaseModel):
    field_id: str
    current_step: int = 0
    answers: Dict[str, Any] = Field(default_factory=dict)
    all_form_answers: Optional[Dict[str, Any]] = Field(default_factory=dict)
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
    document_guidance: Optional[str] = None
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
    document_context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    reply: str
    suggested_questions: List[str] = Field(default_factory=list)
