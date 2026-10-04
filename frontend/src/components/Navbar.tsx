import React from 'react';
import { FileText, Globe, Sparkles, RefreshCw } from 'lucide-react';
import type { Language } from '../types';

interface NavbarProps {
  currentLanguage: Language;
  onLanguageChange: (lang: Language) => void;
  onReset: () => void;
  onLaunchDemo: () => void;
  isDemoMode: boolean;
  isInWorkspace: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentLanguage,
  onLanguageChange,
  onReset,
  onLaunchDemo,
  isDemoMode,
  isInWorkspace,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 bg-white/90 backdrop-blur-md transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={onReset}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20 text-white">
            <FileText className="w-5 h-5 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight text-slate-900 font-['Plus_Jakarta_Sans']">
                FormEase
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200/60 uppercase tracking-wider">
                AI MVP
              </span>
            </div>
            <p className="text-[11px] text-slate-500 hidden sm:block font-medium">
              Understand Any Form. Fill It With Confidence.
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          
          {/* Demo Mode Badge */}
          {isDemoMode && isInWorkspace && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
              Demo Mode
            </span>
          )}

          {/* Quick Demo Button (if on landing or want quick demo) */}
          {!isInWorkspace && (
            <button
              onClick={onLaunchDemo}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:text-blue-600 bg-slate-100/80 hover:bg-blue-50 border border-slate-200/60 transition-all cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Try Demo Form</span>
            </button>
          )}

          {/* New / Reset Form Button (if inside workspace) */}
          {isInWorkspace && (
            <button
              onClick={onReset}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-all cursor-pointer"
              title="Upload another form"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New Form</span>
            </button>
          )}

          {/* Language Selector */}
          <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg p-1 text-xs">
            <Globe className="w-3.5 h-3.5 text-slate-400 ml-1" />
            <button
              onClick={() => onLanguageChange('en')}
              className={`px-2 py-1 rounded font-medium transition-all ${
                currentLanguage === 'en'
                  ? 'bg-white text-blue-700 shadow-xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => onLanguageChange('hi')}
              className={`px-2 py-1 rounded font-medium transition-all ${
                currentLanguage === 'hi'
                  ? 'bg-white text-blue-700 shadow-xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              हिन्दी
            </button>
            <button
              onClick={() => onLanguageChange('mr')}
              className={`px-2 py-1 rounded font-medium transition-all ${
                currentLanguage === 'mr'
                  ? 'bg-white text-blue-700 shadow-xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              मराठी
            </button>
          </div>

        </div>

      </div>
    </header>
  );
};
