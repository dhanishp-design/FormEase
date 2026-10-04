import React, { useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  ListFilter,
  MessageSquare,
  FileCheck
} from 'lucide-react';
import type { FormAnalysisData, FormField, Language } from '../types';
import { DocumentViewer } from './DocumentViewer';
import { FieldAssistantCard } from './FieldAssistantCard';
import { FieldList } from './FieldList';
import { HelpFillModal } from './HelpFillModal';
import { AIChatAssistant } from './AIChatAssistant';
import { ReviewModal } from './ReviewModal';

interface FormAnalyzerProps {
  formData: FormAnalysisData;
  language: Language;
  onUpdateField: (fieldId: string, updates: Partial<FormField>) => void;
  onLanguageChange?: (lang: Language) => void;
}

export const FormAnalyzer: React.FC<FormAnalyzerProps> = ({
  formData,
  language,
  onUpdateField,
}) => {
  // Automatically select Annual Family Income by default (Section 36)
  const defaultFieldId =
    formData.fields.find((f) => f.id === 'field_003')?.id ||
    formData.fields[0]?.id ||
    null;

  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(defaultFieldId);
  const [activeTab, setActiveTab] = useState<'assistant' | 'fields' | 'chat'>('assistant');
  const [helpFillFieldId, setHelpFillFieldId] = useState<string | null>(null);
  const [isGuidedFillingActive, setIsGuidedFillingActive] = useState<boolean>(false);
  const [showReviewModal, setShowReviewModal] = useState<boolean>(false);

  const selectedField = formData.fields.find((f) => f.id === selectedFieldId) || null;
  const helpFillField = formData.fields.find((f) => f.id === helpFillFieldId) || null;

  // Completion stats
  const reviewedCount = formData.fields.filter((f) => f.is_reviewed || f.user_value).length;
  const totalCount = formData.fields.length;
  const progressPct = Math.round((reviewedCount / totalCount) * 100);

  // All session answers map
  const allFormAnswers = formData.fields.reduce((acc, f) => {
    if (f.user_value) acc[f.id] = f.user_value;
    return acc;
  }, {} as Record<string, any>);

  const handleSelectField = (fieldId: string) => {
    setSelectedFieldId(fieldId);
    setActiveTab('assistant');
  };

  const handleApplyHelpValue = (fieldId: string, val: string) => {
    onUpdateField(fieldId, {
      user_value: val,
      is_reviewed: true,
    });
  };

  const handleToggleReviewed = (fieldId: string) => {
    const f = formData.fields.find((item) => item.id === fieldId);
    if (f) {
      onUpdateField(fieldId, { is_reviewed: !f.is_reviewed });
    }
  };

  const handleUpdateValue = (fieldId: string, val: string) => {
    onUpdateField(fieldId, { user_value: val });
  };

  const handleStartGuidedFilling = () => {
    // Find first required field that is not yet reviewed, or first required field
    const nextField =
      formData.fields.find((f) => f.required && !f.is_reviewed && !f.user_value) ||
      formData.fields.find((f) => f.required) ||
      formData.fields[0];

    if (nextField) {
      setSelectedFieldId(nextField.id);
      setHelpFillFieldId(nextField.id);
      setIsGuidedFillingActive(true);
      setActiveTab('assistant');
    }
  };

  const handleNextGuidedField = () => {
    const currentIndex = formData.fields.findIndex((f) => f.id === helpFillFieldId);
    // Find next required unreviewed field in natural document order
    let nextField = formData.fields.slice(currentIndex + 1).find((f) => f.required && !f.is_reviewed);
    if (!nextField) {
      // Check from beginning
      nextField = formData.fields.find((f) => f.required && !f.is_reviewed);
    }

    if (nextField) {
      setSelectedFieldId(nextField.id);
      setHelpFillFieldId(nextField.id);
    } else {
      // Completed all required fields!
      setHelpFillFieldId(null);
      setIsGuidedFillingActive(false);
      setShowReviewModal(true);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] overflow-hidden bg-slate-50">
      
      {/* Top Form Summary & Progress Bar */}
      <div className="bg-white border-b border-slate-200 px-4 sm:px-6 py-3 shrink-0 shadow-2xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3">
          
          {/* Left: Form Title & Detected Badges */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 border border-blue-100">
              <FileCheck className="w-5 h-5 stroke-[2]" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base sm:text-lg font-extrabold text-slate-900 tracking-tight font-['Plus_Jakarta_Sans'] truncate max-w-md">
                  {formData.form_title}
                </h2>
                {formData.is_demo && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                    Demo Mode
                  </span>
                )}
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-500 mt-0.5">
                <span className="font-semibold text-slate-700">
                  {formData.total_fields} fields detected
                </span>
                <span>•</span>
                <span className="text-red-600 font-medium">
                  {formData.required_fields_count} required
                </span>
                <span>•</span>
                <span className="text-slate-500">
                  {formData.optional_fields_count} optional
                </span>
                <span>•</span>
                <span className="text-emerald-700 font-medium hidden sm:inline">
                  Confidence: {Math.round(formData.overall_confidence * 100)}%
                </span>
              </div>
            </div>
          </div>

          {/* Right: Actions, Progress Tracker & Review Button */}
          <div className="flex items-center gap-3">
            
            {/* Start Guided Filling CTA (Section 8) */}
            <button
              onClick={handleStartGuidedFilling}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 transition-all cursor-pointer whitespace-nowrap"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Start Guided Filling</span>
            </button>

            {/* Progress Bar Widget */}
            <div className="hidden lg:flex items-center gap-2.5 bg-slate-50 px-3.5 py-1.5 rounded-xl border border-slate-200">
              <div className="text-right">
                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Form Progress
                </div>
                <div className="text-xs font-bold text-slate-800 font-mono">
                  {reviewedCount} / {totalCount} reviewed
                </div>
              </div>

              <div className="w-24 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-300 rounded-full"
                  style={{ width: `${progressPct}%` }}
                />
              </div>

              <span className="text-xs font-extrabold font-mono text-blue-600">
                {progressPct}%
              </span>
            </div>

            {/* Review Form CTA */}
            <button
              onClick={() => setShowReviewModal(true)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs shadow-sm transition-all cursor-pointer whitespace-nowrap"
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Review Form</span>
            </button>

          </div>

        </div>
      </div>

      {/* Main Workspace Area (Split Desktop Layout) */}
      <div className="flex-1 overflow-hidden p-3 sm:p-4 max-w-7xl w-full mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 sm:gap-4 h-full">
          
          {/* Left Column: Form Preview (7 cols on Desktop) */}
          <div className="lg:col-span-7 h-full flex flex-col min-h-[380px]">
            <DocumentViewer
              documentUrl={formData.document_preview_url || '/demo-form.svg'}
              fields={formData.fields}
              selectedFieldId={selectedFieldId}
              onSelectField={handleSelectField}
            />
          </div>

          {/* Right Column: Assistant & Tooling (5 cols on Desktop) */}
          <div className="lg:col-span-5 h-full flex flex-col min-h-[400px]">
            
            {/* Guided Filling Callout Banner (Section 8) */}
            {reviewedCount < formData.required_fields_count && (
              <div className="mb-2 p-2.5 rounded-xl bg-gradient-to-r from-blue-50/80 to-indigo-50/80 border border-blue-200 flex items-center justify-between gap-2 shrink-0">
                <div className="flex items-center gap-2 overflow-hidden text-left">
                  <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
                  <span className="text-[11px] text-slate-700 font-medium truncate">
                    {formData.required_fields_count} required fields found. Ready to guide you step-by-step.
                  </span>
                </div>
                <button
                  onClick={handleStartGuidedFilling}
                  className="px-2.5 py-1 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-[11px] font-bold shrink-0 transition-all cursor-pointer whitespace-nowrap shadow-2xs"
                >
                  Start Guided Filling
                </button>
              </div>
            )}

            {/* Tab Bar */}
            <div className="flex items-center p-1 bg-white rounded-xl border border-slate-200 mb-2 shrink-0">
              <button
                onClick={() => setActiveTab('assistant')}
                className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                  activeTab === 'assistant'
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Field Assistant</span>
              </button>

              <button
                onClick={() => setActiveTab('fields')}
                className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                  activeTab === 'fields'
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <ListFilter className="w-3.5 h-3.5" />
                <span>Field List ({formData.fields.length})</span>
              </button>

              <button
                onClick={() => setActiveTab('chat')}
                className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                  activeTab === 'chat'
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>AI Chat</span>
              </button>
            </div>

            {/* Tab Views */}
            <div className="flex-1 overflow-hidden">
              {activeTab === 'assistant' && (
                <FieldAssistantCard
                  field={selectedField}
                  language={language}
                  onOpenHelpFill={(fId) => {
                    setHelpFillFieldId(fId);
                    setIsGuidedFillingActive(false);
                  }}
                  onToggleReviewed={handleToggleReviewed}
                  onUpdateValue={handleUpdateValue}
                />
              )}

              {activeTab === 'fields' && (
                <FieldList
                  fields={formData.fields}
                  selectedFieldId={selectedFieldId}
                  onSelectField={handleSelectField}
                />
              )}

              {activeTab === 'chat' && (
                <AIChatAssistant
                  formTitle={formData.form_title}
                  selectedFieldId={selectedFieldId}
                  language={language}
                />
              )}
            </div>

          </div>

        </div>
      </div>

      {/* Help Me Fill / Guided Filling Modal */}
      {helpFillField && (
        <HelpFillModal
          field={helpFillField}
          language={language}
          onClose={() => {
            setHelpFillFieldId(null);
            setIsGuidedFillingActive(false);
          }}
          onApplyValue={handleApplyHelpValue}
          onNextField={handleNextGuidedField}
          hasNextField={Boolean(formData.fields.some((f) => f.required && !f.is_reviewed && f.id !== helpFillField.id))}
          isGuidedMode={isGuidedFillingActive}
          allFormAnswers={allFormAnswers}
        />
      )}

      {/* Final Review Modal */}
      {showReviewModal && (
        <ReviewModal
          fields={formData.fields}
          formTitle={formData.form_title}
          onClose={() => setShowReviewModal(false)}
        />
      )}

    </div>
  );
};
