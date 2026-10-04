import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, Sparkles, FileSearch, ArrowRight } from 'lucide-react';

interface AnalysisProgressProps {
  onComplete: () => void;
  formTitle?: string;
  totalFields?: number;
  isDataReady?: boolean;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  onComplete,
  formTitle,
  totalFields = 12,
  isDataReady = true,
}) => {
  const [currentStep, setCurrentStep] = useState<number>(0);

  const steps = [
    { label: "Reading document", detail: "Extracting optical layout and typography" },
    { label: "Detecting fields", detail: "Locating input zones, labels, and checkboxes" },
    { label: "Understanding instructions", detail: "Analyzing eligibility clauses & required flags" },
    { label: "Preparing explanations", detail: "Synthesizing plain-language guidance & examples" },
  ];

  useEffect(() => {
    // Progress sequentially through the steps
    const timer1 = setTimeout(() => setCurrentStep(1), 500);
    const timer2 = setTimeout(() => setCurrentStep(2), 1100);
    const timer3 = setTimeout(() => setCurrentStep(3), 1700);
    const timer4 = setTimeout(() => setCurrentStep(4), 2300);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, []);

  // When step 4 is reached and data is ready, transition into workspace automatically
  useEffect(() => {
    if (currentStep >= 4 && isDataReady) {
      const redirectTimer = setTimeout(() => {
        onComplete();
      }, 600);
      return () => clearTimeout(redirectTimer);
    }
  }, [currentStep, isDataReady, onComplete]);

  return (
    <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl border border-slate-200 shadow-xl shadow-slate-100 text-center">
      
      {/* Icon Badge */}
      <div className="relative w-16 h-16 mx-auto mb-6">
        <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
          <FileSearch className="w-8 h-8 stroke-[2]" />
        </div>
        <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-md">
          <Sparkles className="w-3.5 h-3.5" />
        </div>
      </div>

      <h3 className="text-xl font-extrabold text-slate-900 tracking-tight font-['Plus_Jakarta_Sans']">
        {formTitle ? formTitle : "Analyzing your form..."}
      </h3>
      <p className="text-xs text-slate-500 mt-1 mb-8">
        Multimodal AI & Nemotron scanning document structure
      </p>

      {/* Steps List */}
      <div className="space-y-4 text-left border-t border-slate-100 pt-6">
        {steps.map((step, idx) => {
          const isDone = currentStep > idx;
          const isCurrent = currentStep === idx;

          return (
            <div
              key={step.label}
              className={`flex items-start gap-3.5 p-2 rounded-xl transition-all ${
                isCurrent ? 'bg-blue-50/60' : ''
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {isDone ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                ) : (
                  <div className="w-5 h-5 rounded-full border-2 border-slate-200" />
                )}
              </div>

              <div>
                <div
                  className={`text-xs font-semibold ${
                    isDone
                      ? 'text-slate-900'
                      : isCurrent
                      ? 'text-blue-900'
                      : 'text-slate-400'
                  }`}
                >
                  {step.label}
                </div>
                <div className="text-[11px] text-slate-400">
                  {step.detail}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Completion & Redirection Area */}
      {currentStep >= 4 && (
        <div className="mt-6 pt-4 border-t border-slate-100 flex flex-col items-center gap-3">
          {isDataReady ? (
            <>
              <div className="w-full flex items-center justify-center gap-2 text-xs font-bold text-emerald-700 bg-emerald-50 py-2.5 px-4 rounded-xl border border-emerald-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Form analyzed • {totalFields} fields detected</span>
              </div>
              <button
                onClick={onComplete}
                className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-xs font-bold rounded-xl shadow-md transition-all flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <span>Open Form Workspace</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </>
          ) : (
            <div className="w-full flex items-center justify-center gap-2 text-xs font-bold text-blue-700 bg-blue-50 py-2.5 px-4 rounded-xl border border-blue-200">
              <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
              <span>Finalizing field extraction...</span>
            </div>
          )}
        </div>
      )}

    </div>
  );
};
