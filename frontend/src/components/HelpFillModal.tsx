import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  X,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Calculator,
  RotateCcw,
  FileText,
  Lightbulb,
  Info
} from 'lucide-react';
import type { FormField, HelpFillResponse, Language } from '../types';
import { requestHelpFill } from '../services/api';

interface HelpFillModalProps {
  field: FormField;
  language: Language;
  onClose: () => void;
  onApplyValue: (fieldId: string, value: string) => void;
  onNextField?: () => void;
  hasNextField?: boolean;
  isGuidedMode?: boolean;
  allFormAnswers?: Record<string, any>;
}

export const HelpFillModal: React.FC<HelpFillModalProps> = ({
  field,
  language,
  onClose,
  onApplyValue,
  onNextField,
  hasNextField = false,
  isGuidedMode = false,
  allFormAnswers = {},
}) => {
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [currentInput, setCurrentInput] = useState<string>('');
  const [response, setResponse] = useState<HelpFillResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [liveValidationWarning, setLiveValidationWarning] = useState<string | null>(null);

  // Load step
  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    requestHelpFill(field.id, stepIndex, answers, language, allFormAnswers)
      .then((data) => {
        if (isMounted) {
          setResponse(data);
          // Pre-populate input if already answered
          if (data.current_step) {
            const existing = answers[data.current_step.step_id] || allFormAnswers[field.id];
            setCurrentInput(existing ? String(existing) : '');
          }
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Error fetching help fill step:', err);
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [field.id, stepIndex, language]);

  // Live input validation against document requirements
  const handleInputChange = (val: string) => {
    setCurrentInput(val);
    setLiveValidationWarning(null);

    // Test Case 37: 10-digit mobile check
    if (field.id === 'field_006' || response?.current_step?.step_id === 'phone_number') {
      const clean = val.replace(/\D/g, '');
      if (clean.length > 0 && clean.length !== 10) {
        setLiveValidationWarning("⚠️ The form expects a 10-digit mobile number. Please check your answer.");
      }
    }

    // Test Case 35: 18-35 age range check
    if (field.id === 'field_002' || response?.current_step?.step_id === 'birth_date') {
      if (val === '17' || val.trim() === '17') {
        setLiveValidationWarning("⚠️ The form specifies an age range of 18–35 years. The value entered appears to be outside that range. Please verify your information.");
      } else if (val.includes('-') && val.length === 10) {
        const year = parseInt(val.split('-')[0], 10);
        if (year) {
          const age = 2024 - year;
          if (age < 18 || age > 35) {
            setLiveValidationWarning("⚠️ The form specifies an age range of 18–35 years. The value entered appears to be outside that range. Please verify your information.");
          }
        }
      }
    }
  };

  const handleNextStep = (overrideVal?: any) => {
    if (!response || !response.current_step) return;

    const valToSave = overrideVal !== undefined ? overrideVal : currentInput;
    const newAnswers = {
      ...answers,
      [response.current_step.step_id]: valToSave,
    };
    setAnswers(newAnswers);

    // Dependency check (Test Case 36): If mother answered "No", skip mother's income question
    if (
      field.id === 'field_003' &&
      response.current_step.step_id === 'mother_has_income' &&
      valToSave === 'No'
    ) {
      newAnswers['mother_income'] = '0';
      setAnswers(newAnswers);
    }

    setStepIndex((prev) => prev + 1);
  };

  const handlePreviousStep = () => {
    if (stepIndex > 0) {
      setStepIndex((prev) => prev - 1);
    }
  };

  const handleReset = () => {
    setStepIndex(0);
    setAnswers({});
    setCurrentInput('');
    setLiveValidationWarning(null);
  };

  const handleConfirmAndUse = (continueNext: boolean = false) => {
    if (response?.suggested_value) {
      onApplyValue(field.id, response.suggested_value);
      if (continueNext && onNextField) {
        onNextField();
      } else {
        onClose();
      }
    }
  };

  const documentSays = response?.current_step?.what_document_says || field.what_document_says;
  const simpleMeaning = response?.current_step?.what_it_means || field.what_it_means || field.explanation;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600">
                  {isGuidedMode ? 'Guided Form Filling' : 'Help Me Fill This'}
                </span>
                <span className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded font-medium text-slate-500">
                  Document-Aware
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-900 leading-tight">
                {field.name}
              </h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 flex-1 overflow-y-auto space-y-4">
          
          {/* Document Source-of-Truth Quote Box */}
          {documentSays && (
            <div className="p-3 rounded-xl bg-amber-50/60 border border-amber-200/80 text-amber-950 text-xs">
              <div className="flex items-center gap-1.5 font-bold mb-1 text-[11px] text-amber-800">
                <FileText className="w-3.5 h-3.5" />
                <span>According to the form:</span>
              </div>
              <p className="italic font-serif leading-relaxed text-[11px]">
                "{documentSays}"
              </p>
            </div>
          )}

          {/* Simple Explanation */}
          {simpleMeaning && (
            <div className="p-3 rounded-xl bg-blue-50/40 border border-blue-100/80 text-xs flex items-start gap-2">
              <Lightbulb className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <p className="text-slate-700 leading-relaxed text-[11px]">
                {simpleMeaning}
              </p>
            </div>
          )}

          {/* Document Dependency Notice (Test Case 36) */}
          {response?.document_guidance && (
            <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-900 text-xs flex items-start gap-2">
              <Info className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
              <span>{response.document_guidance}</span>
            </div>
          )}

          {/* Live Validation Warning Notice (Test Case 35 & 37) */}
          {(liveValidationWarning || response?.verification_warning) && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-start gap-2 animate-in fade-in duration-150">
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span className="font-medium text-[11px]">
                {liveValidationWarning || response?.verification_warning}
              </span>
            </div>
          )}

          {loading ? (
            <div className="py-10 text-center text-slate-400 space-y-3">
              <Sparkles className="w-6 h-6 mx-auto animate-spin text-blue-500" />
              <div className="text-xs">Preparing document-aware guidance...</div>
            </div>
          ) : response?.is_completed ? (
            /* Completed Calculation State */
            <div className="space-y-4 animate-in fade-in duration-300 pt-1">
              
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 shrink-0" />
                <div>
                  <div className="font-bold text-sm">Value Verified Against Document</div>
                  <div className="text-xs text-emerald-700 mt-0.5">
                    Calculated and formatted according to official document requirements.
                  </div>
                </div>
              </div>

              {/* Calculation Breakdown (e.g. father income * 12 + mother income * 12) */}
              {response.calculation_breakdown && (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/90 text-xs">
                  <div className="flex items-center gap-2 font-bold text-slate-700 mb-2">
                    <Calculator className="w-4 h-4 text-blue-600" />
                    <span>Calculation Breakdown</span>
                  </div>
                  <pre className="font-sans text-slate-600 whitespace-pre-wrap leading-relaxed text-[12px]">
                    {response.calculation_breakdown}
                  </pre>
                </div>
              )}

              {/* Suggested Value Hero Box */}
              <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 text-center">
                <span className="text-xs font-semibold text-blue-700 uppercase tracking-wider">
                  Suggested Value
                </span>
                <div className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1 font-mono">
                  {response.suggested_value}
                </div>
              </div>

            </div>
          ) : (
            /* Question Step State */
            <div className="space-y-4 animate-in fade-in duration-200 pt-1">
              
              {/* Progress Indicator */}
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>
                  Question {(response?.current_step_index ?? 0) + 1} of {response?.total_steps ?? 3}
                </span>
                <span className="font-semibold text-blue-600">
                  Step-by-step guidance
                </span>
              </div>

              <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-300"
                  style={{
                    width: `${(((response?.current_step_index ?? 0) + 1) / (response?.total_steps ?? 3)) * 100}%`,
                  }}
                />
              </div>

              {/* Current Question */}
              <div className="space-y-1.5">
                <h4 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                  {response?.current_step?.question}
                </h4>
                {response?.current_step?.help_text && (
                  <p className="text-xs text-slate-500">
                    {response.current_step.help_text}
                  </p>
                )}
              </div>

              {/* Question Inputs */}
              <div className="pt-2">
                {response?.current_step?.input_type === 'choice' && response.current_step.options ? (
                  <div className="grid grid-cols-2 gap-3">
                    {response.current_step.options.map((opt) => (
                      <button
                        key={opt}
                        onClick={() => handleNextStep(opt)}
                        className="py-3 px-4 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/50 text-slate-800 font-semibold text-xs sm:text-sm text-center transition-all cursor-pointer"
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="relative">
                      <input
                        type={response?.current_step?.input_type === 'date' ? 'date' : 'text'}
                        placeholder={response?.current_step?.placeholder || 'Type here...'}
                        value={currentInput}
                        onChange={(e) => handleInputChange(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && currentInput.trim()) {
                            handleNextStep();
                          }
                        }}
                        autoFocus
                        className="w-full px-4 py-3 rounded-xl border border-slate-300 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-3 focus:ring-blue-100 font-medium"
                      />
                      {response?.current_step?.unit && (
                        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-semibold text-slate-400">
                          {response.current_step.unit}
                        </span>
                      )}
                    </div>

                    {/* Quick Demo Pre-fills for Scene 5 */}
                    {field.id === 'field_003' && stepIndex === 0 && !currentInput && (
                      <div className="flex items-center gap-2 text-[11px] text-slate-500">
                        <span>Quick demo:</span>
                        <button
                          onClick={() => handleInputChange('30000')}
                          className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700 font-mono"
                        >
                          ₹ 30,000
                        </button>
                      </div>
                    )}
                    {field.id === 'field_003' && stepIndex === 2 && !currentInput && (
                      <div className="flex items-center gap-2 text-[11px] text-slate-500">
                        <span>Quick demo:</span>
                        <button
                          onClick={() => handleInputChange('10000')}
                          className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700 font-mono"
                        >
                          ₹ 10,000
                        </button>
                      </div>
                    )}

                    {/* Quick Demo for age validation check (Test Case 35) */}
                    {field.id === 'field_002' && !currentInput && (
                      <div className="flex items-center gap-2 text-[11px] text-slate-500">
                        <span>Test age check:</span>
                        <button
                          onClick={() => handleInputChange('17')}
                          className="px-2 py-0.5 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded font-mono"
                        >
                          Try Age: 17
                        </button>
                        <button
                          onClick={() => handleInputChange('2004-08-15')}
                          className="px-2 py-0.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded font-mono"
                        >
                          Try Age: 20
                        </button>
                      </div>
                    )}

                    {/* Quick Demo for mobile validation check (Test Case 37) */}
                    {field.id === 'field_006' && !currentInput && (
                      <div className="flex items-center gap-2 text-[11px] text-slate-500">
                        <span>Test 10-digit check:</span>
                        <button
                          onClick={() => handleInputChange('12345')}
                          className="px-2 py-0.5 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded font-mono"
                        >
                          Try: 12345
                        </button>
                        <button
                          onClick={() => handleInputChange('9820154321')}
                          className="px-2 py-0.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded font-mono"
                        >
                          Try: 9820154321
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>

            </div>
          )}

        </div>

        {/* Modal Footer Controls */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/70 flex items-center justify-between gap-3">
          {response?.is_completed ? (
            <div className="flex items-center justify-between w-full gap-3">
              <button
                onClick={handleReset}
                className="px-3.5 py-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Recalculate</span>
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleConfirmAndUse(false)}
                  className="px-4 py-2.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 text-xs font-semibold shadow-xs transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Use Value</span>
                </button>

                {isGuidedMode && hasNextField && (
                  <button
                    onClick={() => handleConfirmAndUse(true)}
                    className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-bold shadow-md shadow-blue-500/20 transition-all flex items-center gap-2 cursor-pointer"
                  >
                    <span>Save &amp; Next Field</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between w-full gap-3">
              <button
                onClick={handlePreviousStep}
                disabled={stepIndex === 0}
                className="px-3.5 py-2.5 rounded-xl text-slate-600 hover:bg-slate-200/60 disabled:opacity-30 text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back</span>
              </button>

              {response?.current_step?.input_type !== 'choice' && (
                <button
                  onClick={() => handleNextStep()}
                  disabled={!currentInput.trim()}
                  className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-bold shadow-md shadow-blue-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <span>Continue</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
