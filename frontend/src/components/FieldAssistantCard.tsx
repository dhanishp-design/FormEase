import React from 'react';
import {
  Sparkles,
  CheckCircle2,
  Lightbulb,
  PenTool,
  ShieldAlert,
  BookOpen,
  FileText,
  Tag
} from 'lucide-react';
import type { FormField, Language } from '../types';

interface FieldAssistantCardProps {
  field: FormField | null;
  language?: Language;
  onOpenHelpFill: (fieldId: string) => void;
  onToggleReviewed: (fieldId: string) => void;
  onUpdateValue: (fieldId: string, value: string) => void;
}

export const FieldAssistantCard: React.FC<FieldAssistantCardProps> = ({
  field,
  onOpenHelpFill,
  onToggleReviewed,
  onUpdateValue,
}) => {
  if (!field) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-400">
        <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-500 flex items-center justify-center mb-3">
          <BookOpen className="w-6 h-6 stroke-[1.8]" />
        </div>
        <h4 className="text-sm font-bold text-slate-700">No Field Selected</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-xs">
          Click any field on the document preview to inspect its meaning, required format, and step-by-step guidance.
        </p>
      </div>
    );
  }

  // Confidence calculations
  const confPercent = Math.round(field.confidence * 100);
  const confLevel =
    confPercent >= 90
      ? { label: 'High confidence', color: 'text-emerald-700 bg-emerald-50 border-emerald-200' }
      : confPercent >= 70
      ? { label: 'Medium confidence', color: 'text-amber-700 bg-amber-50 border-amber-200' }
      : { label: 'Needs verification', color: 'text-rose-700 bg-rose-50 border-rose-200' };

  const documentSays = field.what_document_says || field.what_to_enter;
  const simpleMeaning = field.what_it_means || field.explanation;
  const userMustProvide = field.what_user_should_provide || field.what_to_enter;

  return (
    <div className="h-full flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      
      {/* Top Card Header */}
      <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-start justify-between gap-3">
        <div>
          <div className="text-[10px] font-bold text-blue-600 uppercase tracking-wider">
            {field.section}
          </div>
          <h3 className="text-base sm:text-lg font-extrabold text-slate-900 tracking-tight mt-0.5 font-['Plus_Jakarta_Sans']">
            {field.name}
          </h3>
        </div>

        {/* Required Badge */}
        <div className="shrink-0 flex items-center gap-1.5">
          {field.required ? (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-50 text-red-700 border border-red-200 uppercase tracking-wide">
              Required
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200 uppercase tracking-wide">
              Requirement not specified
            </span>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
        
        {/* Sensitive Information Warning Banner */}
        {field.sensitive && (
          <div className="p-3 rounded-xl bg-amber-50/80 border border-amber-200/90 text-amber-900">
            <div className="flex items-center gap-2 font-bold text-xs">
              <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
              <span>Sensitive Information Advisory</span>
            </div>
            <p className="mt-1 text-[11px] text-amber-800 leading-relaxed">
              FormEase can explain this field, but it cannot verify whether your information is legally correct. Please verify the final value before submitting.
            </p>
          </div>
        )}

        {/* Section 1: What the Form Says (Document Source of Truth) */}
        {documentSays && (
          <div className="p-3.5 rounded-xl bg-amber-50/40 border border-amber-200/70">
            <div className="flex items-center gap-2 font-bold text-amber-950 text-xs mb-1">
              <FileText className="w-3.5 h-3.5 text-amber-700" />
              <span>📄 According to the Form:</span>
            </div>
            <p className="text-amber-900/90 italic leading-relaxed text-[12px] font-serif">
              "{documentSays}"
            </p>
          </div>
        )}

        {/* Section 1b: Document Instruction (Part 14) */}
        {field.document_instruction && (
          <div className="p-3 rounded-xl bg-purple-50/60 border border-purple-200/80 text-purple-950 text-xs flex items-start gap-2">
            <FileText className="w-4 h-4 text-purple-700 shrink-0 mt-0.5" />
            <div className="text-[11px] leading-relaxed">
              <span className="font-bold text-purple-900">📋 Form Instruction: </span>
              <span>{field.document_instruction}</span>
            </div>
          </div>
        )}

        {/* Section 2: In Simple Words */}
        <div className="p-3.5 rounded-xl bg-blue-50/40 border border-blue-100/80">
          <div className="flex items-center gap-2 font-bold text-slate-900 text-xs mb-1.5">
            <Lightbulb className="w-4 h-4 text-blue-600" />
            <span>💡 In Simple Words:</span>
          </div>
          <p className="text-slate-700 leading-relaxed text-[12px]">
            {simpleMeaning}
          </p>
        </div>

        {/* Section 3: What to Enter */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
          <div className="flex items-center gap-2 font-bold text-slate-900 text-xs mb-1.5">
            <PenTool className="w-4 h-4 text-indigo-600" />
            <span>✏️ What should you enter?</span>
          </div>
          <p className="text-slate-700 leading-relaxed text-[12px]">
            {userMustProvide}
          </p>
          
          {field.expected_format && (
            <div className="mt-2 text-[11px] text-slate-500 flex items-center gap-1.5">
              <span className="font-semibold text-slate-600">Expected format:</span>
              <span className="font-mono bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-700">
                {field.expected_format}
              </span>
            </div>
          )}
        </div>

        {/* Allowed options if document provides them */}
        {field.allowed_values && field.allowed_values.length > 0 && (
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
            <div className="flex items-center gap-1.5 font-bold text-slate-700 text-[11px]">
              <Tag className="w-3.5 h-3.5 text-blue-600" />
              <span>Allowed options from document:</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {field.allowed_values.map((opt) => (
                <span
                  key={opt}
                  className="px-2 py-0.5 rounded-md bg-white border border-slate-200 text-slate-700 font-medium text-[11px]"
                >
                  {opt}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Form Placeholder (Part 10) */}
        {field.placeholder && (
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 text-xs flex items-center justify-between">
            <span className="font-semibold text-slate-500 text-[11px]">🏷️ Form Placeholder:</span>
            <span className="font-mono font-medium text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200 text-xs">
              {field.placeholder}
            </span>
          </div>
        )}

        {/* Section 4: Example from Form (Part 11) */}
        {(field.document_example || field.example) && (
          <div className="p-3 rounded-xl bg-slate-100/60 border border-slate-200/60 flex items-center justify-between">
            <span className="font-semibold text-slate-500 text-[11px]">Example from form:</span>
            <span className="font-mono font-bold text-slate-800 bg-white px-2 py-0.5 rounded border border-slate-200 text-xs">
              {field.document_example || field.example}
            </span>
          </div>
        )}

        {/* Confidence & Type strip */}
        <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-100">
          <span className="text-slate-500">AI Confidence:</span>
          <span className={`px-2 py-0.5 rounded-full font-semibold border ${confLevel.color}`}>
            {confPercent}% • {confLevel.label}
          </span>
        </div>

        {/* Value Review / Stored value (Part 9 & 29) */}
        <div className="pt-2 border-t border-slate-100">
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">
            Your value:
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder={field.placeholder || "Enter your answer..."}
              value={field.user_value || ''}
              onChange={(e) => onUpdateValue(field.id, e.target.value)}
              className="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-xs text-slate-900 focus:bg-white focus:outline-none focus:border-blue-500 font-medium"
            />
            <button
              onClick={() => onToggleReviewed(field.id)}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer ${
                field.is_reviewed
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
              }`}
              title="Toggle reviewed status"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{field.is_reviewed ? 'Reviewed' : 'Mark Done'}</span>
            </button>
          </div>
        </div>

      </div>

      {/* Prominent Help Me Fill CTA */}
      <div className="p-3.5 border-t border-slate-200 bg-slate-50/80 shrink-0">
        <button
          onClick={() => onOpenHelpFill(field.id)}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-xs sm:text-sm shadow-md shadow-blue-500/20 transition-all flex items-center justify-center gap-2 transform active:scale-[0.99] cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          <span>Help Me Fill This</span>
        </button>
      </div>

    </div>
  );
};
