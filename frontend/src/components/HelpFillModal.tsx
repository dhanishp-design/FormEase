import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  X,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Calculator,
  RotateCcw
} from 'lucide-react';
import type { FormField, HelpFillResponse, Language } from '../types';
import { requestHelpFill } from '../services/api';

interface HelpFillModalProps {
  field: FormField;
  language: Language;
  onClose: () => void;
  onApplyValue: (fieldId: string, value: string) => void;
}

export const HelpFillModal: React.FC<HelpFillModalProps> = ({
  field,
  language,
  onClose,
  onApplyValue,
}) => {
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [currentInput, setCurrentInput] = useState<string>('');
  const [response, setResponse] = useState<HelpFillResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Load step
  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    requestHelpFill(field.id, stepIndex, answers, language)
      .then((data) => {
        if (isMounted) {
          setResponse(data);
          // Pre-populate input if already answered
          if (data.current_step) {
            const existing = answers[data.current_step.step_id];
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

  const handleNextStep = (overrideVal?: any) => {
    if (!response || !response.current_step) return;

    const valToSave = overrideVal !== undefined ? overrideVal : currentInput;
    const newAnswers = {
      ...answers,
      [response.current_step.step_id]: valToSave,
    };
    setAnswers(newAnswers);

    // If Annual Income and mother answered "No", skip to calculate
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
  };

  const handleConfirmAndUse = () => {
    if (response?.suggested_value) {
      onApplyValue(field.id, response.suggested_value);
      onClose();
    }
  };

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
              <div className="text-[11px] font-bold uppercase tracking-wider text-blue-600">
                Help Me Fill This
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
        <div className="p-6 flex-1 overflow-y-auto space-y-6">
          
          {loading ? (
            <div className="py-12 text-center text-slate-400 space-y-3">
              <Sparkles className="w-6 h-6 mx-auto animate-spin text-blue-500" />
              <div className="text-xs">Preparing smart questions...</div>
            </div>
          ) : response?.is_completed ? (
            /* Completed Calculation State */
            <div className="space-y-5 animate-in fade-in duration-300">
              
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 shrink-0" />
                <div>
                  <div className="font-bold text-sm">Smart Suggestion Ready</div>
                  <div className="text-xs text-emerald-700 mt-0.5">
                    We've calculated the exact value according to standard form requirements.
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

              {/* Legal Warning Notice */}
              <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-800 text-[11px] leading-relaxed flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <span>{response.verification_warning}</span>
              </div>

            </div>
          ) : (
            /* Question Step State */
            <div className="space-y-5 animate-in fade-in duration-200">
              
              {/* Progress Indicator */}
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>
                  Question {(response?.current_step_index ?? 0) + 1} of {response?.total_steps ?? 3}
                </span>
                <span className="font-semibold text-blue-600">
                  Step-by-step assistant
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
                        onChange={(e) => setCurrentInput(e.target.value)}
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
                          onClick={() => setCurrentInput('30000')}
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
                          onClick={() => setCurrentInput('10000')}
                          className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700 font-mono"
                        >
                          ₹ 10,000
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

              <button
                onClick={handleConfirmAndUse}
                className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-bold shadow-md shadow-blue-500/20 transition-all flex items-center gap-2 cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Use This Value</span>
              </button>
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
