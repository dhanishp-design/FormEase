export type Language = 'en' | 'hi' | 'mr';

export interface BoundingBox {
  x: number;      // percentage (0-100)
  y: number;      // percentage (0-100)
  width: number;  // percentage (0-100)
  height: number; // percentage (0-100)
}

export interface FormField {
  id: string;
  name: string;
  type: string;
  required: boolean;
  page: number;
  section: string;
  explanation: string;
  what_to_enter: string;
  example: string;
  confidence: number;
  sensitive: boolean;
  bbox?: BoundingBox;
  user_value?: string;
  is_reviewed?: boolean;
}

export interface FormAnalysisData {
  form_id: string;
  form_title: string;
  summary: string;
  total_fields: number;
  required_fields_count: number;
  optional_fields_count: number;
  overall_confidence: number;
  language: Language;
  is_demo: boolean;
  document_preview_url?: string;
  fields: FormField[];
}

export interface HelpFillStep {
  step_id: string;
  question: string;
  help_text?: string;
  input_type: string;
  placeholder?: string;
  options?: string[];
  unit?: string;
}

export interface HelpFillResponse {
  field_id: string;
  field_name: string;
  current_step_index: number;
  total_steps: number;
  current_step?: HelpFillStep;
  is_completed: boolean;
  calculation_breakdown?: string;
  suggested_value?: string;
  verification_warning?: string;
  language: Language;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  reply: string;
  suggested_questions: string[];
}
