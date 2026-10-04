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
  label?: string;
  type: string;
  required: boolean;
  page: number;
  section: string;
  
  // Document Source-of-Truth enhancements
  what_document_says?: string;
  what_it_means?: string;
  what_user_should_provide?: string;
  expected_format?: string;
  allowed_values?: string[];
  min_value?: string;
  max_value?: string;
  example_from_document?: string;
  validation_rules?: string[];
  dependencies?: any[];
  related_fields?: string[];

  explanation: string;
  what_to_enter: string;
  example: string;
  confidence: number;
  sensitive: boolean;
  bbox?: BoundingBox;
  user_value?: string;
  is_reviewed?: boolean;
}

export interface DocumentInstruction {
  text: string;
  page: number;
  importance: 'high' | 'medium' | 'low';
}

export interface FormAnalysisData {
  form_id: string;
  form_title: string;
  purpose?: string;
  organization?: string;
  summary: string;
  total_fields: number;
  required_fields_count: number;
  optional_fields_count: number;
  overall_confidence: number;
  language: Language;
  is_demo: boolean;
  document_preview_url?: string;
  instructions?: DocumentInstruction[];
  sections?: Array<{ id: string; name: string; page: number }>;
  fields: FormField[];
}

export interface HelpFillStep {
  step_id: string;
  question: string;
  what_document_says?: string;
  what_it_means?: string;
  help_text?: string;
  input_type: string;
  placeholder?: string;
  options?: string[];
  unit?: string;
  validation_rule?: string;
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
  document_guidance?: string;
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
