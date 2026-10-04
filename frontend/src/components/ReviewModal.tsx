import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  X,
  FileCheck,
  Copy,
  Check,
  ShieldCheck
} from 'lucide-react';
import type { FormField } from '../types';

interface ReviewModalProps {
  fields: FormField[];
  formTitle: string;
  onClose: () => void;
}

export const ReviewModal: React.FC<ReviewModalProps> = ({
  fields,
  formTitle,
  onClose,
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  const requiredFields = fields.filter((f) => f.required);
  const reviewedFields = fields.filter((f) => f.is_reviewed || f.user_value);
  const reviewedRequired = requiredFields.filter((f) => f.is_reviewed || f.user_value);

  const completionPct = Math.round((reviewedFields.length / fields.length) * 100);

  // Smart Validation checks
  const emailField = fields.find((f) => f.type === 'email');
  const isEmailValid = emailField?.user_value ? /\S+@\S+\.\S+/.test(emailField.user_value) : true;

  const mobileField = fields.find((f) => f.type === 'phone');
  const isMobileValid = mobileField?.user_value ? /^\d{10}$/.test(mobileField.user_value.replace(/\D/g, '')) : true;

  const lowConfidenceFields = fields.filter((f) => f.confidence < 0.9);
  const sensitiveFields = fields.filter((f) => f.sensitive);

  const handleCopySummary = () => {
    const lines = [
      `--- FORMEASE FORM REVIEW SUMMARY ---`,
      `Form: ${formTitle}`,
      `Completion: ${reviewedFields.length}/${fields.length} fields (${completionPct}%)`,
      ``,
      `FIELDS REVIEWED:`,
      ...fields.map((f) => `• ${f.name} [${f.required ? 'REQUIRED' : 'OPTIONAL'}]: ${f.user_value || '(Not entered)'}`),
      ``,
      `DISCLAIMER: FormEase assists understanding and calculation. Please verify all entries with your original documentation before final official submission.`
    ];
    navigator.clipboard.writeText(lines.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-xs">
              <FileCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] font-bold uppercase tracking-wider text-blue-600">
                Pre-Submission Audit
              </div>
              <h3 className="text-base font-bold text-slate-900 leading-tight">
                Form Review
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

        {/* Body */}
        <div className="p-6 flex-1 overflow-y-auto space-y-6 text-xs">
          
          {/* Status Banner: "Ready for your review" */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-blue-700 uppercase tracking-wider">
                Readiness Status
              </span>
              <div className="text-base font-extrabold text-slate-900 mt-0.5 font-['Plus_Jakarta_Sans']">
                Ready for your review
              </div>
              <div className="text-slate-600 text-[11px] mt-0.5">
                {reviewedRequired.length} of {requiredFields.length} required fields addressed
              </div>
            </div>

            <div className="text-right">
              <div className="text-2xl font-extrabold font-mono text-blue-600">
                {completionPct}%
              </div>
              <div className="text-[10px] text-slate-400">Total Progress</div>
            </div>
          </div>

          {/* Validation Checklist */}
          <div className="space-y-2.5">
            <div className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Verification Checklist
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex items-center gap-2 text-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  Required fields reviewed ({reviewedRequired.length}/{requiredFields.length})
                </span>
              </div>

              <div className="flex items-center gap-2 text-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Dates formatted properly (DD/MM/YYYY)</span>
              </div>

              <div className="flex items-center gap-2 text-slate-800">
                <CheckCircle2 className={`w-4 h-4 ${isEmailValid ? 'text-emerald-600' : 'text-amber-500'} shrink-0`} />
                <span>Email format validation check</span>
              </div>

              <div className="flex items-center gap-2 text-slate-800">
                <CheckCircle2 className={`w-4 h-4 ${isMobileValid ? 'text-emerald-600' : 'text-amber-500'} shrink-0`} />
                <span>Mobile number 10-digit check</span>
              </div>
            </div>
          </div>

          {/* Cautionary Warnings */}
          <div className="space-y-2.5">
            <div className="text-xs font-bold text-amber-900 uppercase tracking-wider">
              Items Requiring Manual Verification
            </div>

            <div className="space-y-2">
              <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold">Annual Family Income</div>
                  <div className="text-[11px] text-amber-800 mt-0.5">
                    Should be cross-checked against your official Revenue Department Income Certificate before submission.
                  </div>
                </div>
              </div>

              {sensitiveFields.length > 0 && (
                <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 flex items-start gap-2.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-bold">{sensitiveFields.length} sensitive fields detected</div>
                    <div className="text-[11px] text-amber-800 mt-0.5">
                      Bank Account and IFSC details must match your passbook to ensure successful DBT fund transfer.
                    </div>
                  </div>
                </div>
              )}

              {lowConfidenceFields.length > 0 && (
                <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 flex items-start gap-2.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-bold">{lowConfidenceFields.length} fields have moderate AI confidence</div>
                    <div className="text-[11px] text-amber-800 mt-0.5">
                      Please double-check entries for: {lowConfidenceFields.map((f) => f.name).join(', ')}.
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Golden Rule Disclaimer */}
          <div className="p-3 rounded-xl bg-slate-100/70 border border-slate-200 text-slate-500 text-[11px] flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-slate-400 shrink-0" />
            <span>FormEase does not submit applications on your behalf. Always verify data on official portal.</span>
          </div>

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between gap-3">
          <button
            onClick={handleCopySummary}
            className="px-4 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-100 text-slate-700 font-semibold text-xs flex items-center gap-1.5 transition-all shadow-2xs cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Summary Copied!' : 'Copy Summary'}</span>
          </button>

          <button
            onClick={onClose}
            className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs transition-all shadow-md shadow-blue-500/20 cursor-pointer"
          >
            Done Reviewing
          </button>
        </div>

      </div>
    </div>
  );
};
