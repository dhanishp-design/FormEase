import React from 'react';
import {
  Sparkles,
  CheckCircle2,
  Lightbulb,
  PenTool,
  ShieldAlert,
  BookOpen
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
              Optional
            </span>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        
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

        {/* Section 1: Meaning */}
        <div className="p-3.5 rounded-xl bg-blue-50/40 border border-blue-100/80">
          <div className="flex items-center gap-2 font-bold text-slate-900 text-xs mb-1.5">
            <Lightbulb className="w-4 h-4 text-blue-600" />
            <span>💡 What does this mean?</span>
          </div>
          <p className="text-slate-700 leading-relaxed text-[12px]">
            {field.explanation}
          </p>
        </div>

        {/* Section 2: What to enter */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
          <div className="flex items-center gap-2 font-bold text-slate-900 text-xs mb-1.5">
            <PenTool className="w-4 h-4 text-indigo-600" />
            <span>✏️ What should you enter?</span>
          </div>
          <p className="text-slate-700 leading-relaxed text-[12px]">
            {field.what_to_enter}
          </p>
        </div>

        {/* Section 3: Example */}
        {field.example && (
          <div className="p-3 rounded-xl bg-slate-100/60 border border-slate-200/60 flex items-center justify-between">
            <span className="font-semibold text-slate-500 text-[11px]">Example:</span>
            <span className="font-mono font-bold text-slate-800 bg-white px-2 py-0.5 rounded border border-slate-200 text-xs">
              {field.example}
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

        {/* Value Review / Stored value */}
        <div className="pt-2 border-t border-slate-100">
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">
            Your verified value for this field:
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder={field.example || "Enter or compute value..."}
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
