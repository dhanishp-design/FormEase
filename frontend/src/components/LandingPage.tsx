import React from 'react';
import {
  UploadCloud,
  Sparkles,
  ShieldCheck,
  Languages,
  CheckCircle2,
  FileSearch,
  Eye,
  SlidersHorizontal
} from 'lucide-react';
import type { Language } from '../types';

interface LandingPageProps {
  onStartUpload: () => void;
  onLaunchDemo: () => void;
  language: Language;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartUpload,
  onLaunchDemo,
  language,
}) => {
  const t = {
    en: {
      tagline: 'Understand Any Form. Fill It With Confidence.',
      subhead: 'Upload complicated forms and let AI explain every field in simple language.',
      ctaUpload: 'Analyze My Form',
      ctaDemo: 'Explore Demo Form',
      trust: 'AI-powered assistance. Human-reviewed decisions.',
      trustSub: 'FormEase helps you understand forms. Always verify important information before submitting.',
      howItWorksTitle: 'How It Works',
      step1Title: '01 Upload',
      step1Desc: 'Upload your PDF or image (scholarship, government, admissions, or banking).',
      step2Title: '02 Understand',
      step2Desc: 'Click or highlight any field. AI breaks down complex legal wording into plain terms.',
      step3Title: '03 Fill',
      step3Desc: 'Get interactive, conversational step-by-step help with automated calculation.',
    },
    hi: {
      tagline: 'किसी भी फॉर्म को समझें। आत्मविश्वास के साथ भरें।',
      subhead: 'जटिल फॉर्म अपलोड करें और AI को हर फ़ील्ड को आसान भाषा में समझाने दें।',
      ctaUpload: 'अपना फॉर्म विश्लेषित करें',
      ctaDemo: 'डेमो फॉर्म देखें',
      trust: 'AI-संचालित सहायता। मानव-सत्यापित निर्णय।',
      trustSub: 'FormEase आपको फॉर्म समझने में मदद करता है। सबमिट करने से पहले हमेशा महत्वपूर्ण जानकारी सत्यापित करें।',
      howItWorksTitle: 'यह कैसे काम करता है',
      step1Title: '01 अपलोड करें',
      step1Desc: 'अपना PDF या फ़ोटो अपलोड करें।',
      step2Title: '02 समझें',
      step2Desc: 'किसी भी फ़ील्ड पर क्लिक करें और सरल स्पष्टीकरण पाएं।',
      step3Title: '03 भरें',
      step3Desc: 'चरण-दर-चरण मार्गदर्शन और गणनाओं के साथ आसानी से भरें।',
    },
    mr: {
      tagline: 'कोणताही अर्ज सहज समजून घ्या. आत्मविश्वासाने भरा.',
      subhead: 'क्लिष्ट अर्ज अपलोड करा आणि AI ला प्रत्येक रकाना सोप्या भाषेत समजावून सांगू द्या.',
      ctaUpload: 'माझा अर्ज तपासा',
      ctaDemo: 'डेमो अर्ज पहा',
      trust: 'AI-आधारित मदत. मानवी पडताळणी.',
      trustSub: 'FormEase तुम्हाला अर्ज समजून घेण्यास मदत करते. सबमिट करण्यापूर्वी मूळ कागदपत्रांशी खात्री करा.',
      howItWorksTitle: 'हे कसे कार्य करते',
      step1Title: '०१ अपलोड करा',
      step1Desc: 'तुमचा PDF किंवा फोटो अपलोड करा.',
      step2Title: '०२ समजून घ्या',
      step2Desc: 'कोणत्याही रकान्यावर क्लिक करा आणि सोपा अर्थ जाणून घ्या.',
      step3Title: '०३ भरा',
      step3Desc: 'स्मार्ट प्रश्नांच्या साहाय्याने अचूक रक्कम व माहिती भरा.',
    }
  }[language];

  return (
    <div className="min-h-screen bg-slate-50/70 text-slate-900 flex flex-col justify-between">
      
      {/* Hero Section */}
      <section className="relative pt-16 pb-20 md:pt-24 md:pb-28 overflow-hidden">
        
        {/* Subtle background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-100/50 rounded-full blur-3xl pointer-events-none -z-10" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          
          {/* Top Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200/80 text-blue-700 text-xs font-semibold shadow-xs mb-8">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>Multimodal AI Form Intelligence</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 font-['Plus_Jakarta_Sans'] leading-[1.1] mb-6">
            Understand Any Form.{' '}
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text text-transparent">
              Fill It With Confidence.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="max-w-2xl mx-auto text-lg sm:text-xl text-slate-600 leading-relaxed font-normal mb-10">
            {t.subhead}
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto">
            <button
              onClick={onStartUpload}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-base shadow-lg shadow-blue-500/25 transition-all transform hover:-translate-y-0.5 cursor-pointer"
            >
              <UploadCloud className="w-5 h-5 stroke-[2.2]" />
              <span>{t.ctaUpload}</span>
            </button>
            <button
              onClick={onLaunchDemo}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 font-semibold text-base border border-slate-200/90 shadow-xs hover:border-slate-300 transition-all cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>{t.ctaDemo}</span>
            </button>
          </div>

          {/* Trust strip */}
          <div className="mt-8 flex items-center justify-center gap-2 text-xs text-slate-500">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>{t.trust}</span>
          </div>

          {/* Killer Feature Teaser / Visual Mockup */}
          <div className="mt-14 relative max-w-4xl mx-auto rounded-2xl border border-slate-200/90 bg-white p-2.5 sm:p-4 shadow-xl shadow-slate-200/60 text-left">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 px-3 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-400 inline-block"></span>
                <span className="w-3 h-3 rounded-full bg-amber-400 inline-block"></span>
                <span className="w-3 h-3 rounded-full bg-emerald-400 inline-block"></span>
                <span className="ml-2 font-medium text-slate-600">FormEase Workspace Preview</span>
              </div>
              <span className="text-[11px] bg-slate-100 px-2 py-0.5 rounded font-mono">Split Document + Assistant UI</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 pt-3">
              {/* Left document mockup */}
              <div className="md:col-span-7 bg-slate-50 rounded-xl p-4 border border-slate-200/80 relative">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Form Document (Left)</div>
                <div className="bg-white rounded-lg p-3.5 shadow-xs border border-slate-200 text-xs space-y-2">
                  <div className="font-bold text-slate-800 border-b pb-1 text-sm">Post-Matric Scholarship 2024-25</div>
                  <div className="flex justify-between items-center py-1">
                    <span className="text-slate-500">Applicant Name</span>
                    <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded">PRIYA RAMESH SHARMA</span>
                  </div>
                  {/* Highlighted box */}
                  <div className="relative p-2 rounded-lg bg-blue-50/80 border-2 border-blue-500 ring-4 ring-blue-500/10 transition-all">
                    <div className="flex justify-between items-center text-blue-950 font-semibold">
                      <span>Annual Family Income *</span>
                      <span className="bg-blue-600 text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">Selected</span>
                    </div>
                    <div className="text-[11px] text-blue-700 mt-1">₹ 4,80,000</div>
                  </div>
                  <div className="flex justify-between items-center py-1">
                    <span className="text-slate-500">Domicile State</span>
                    <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded">Maharashtra</span>
                  </div>
                </div>
              </div>

              {/* Right assistant mockup */}
              <div className="md:col-span-5 bg-gradient-to-b from-blue-50/40 to-slate-50 rounded-xl p-4 border border-blue-100 flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-1.5 text-xs font-bold text-blue-700 mb-2">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>FIELD ASSISTANT (RIGHT)</span>
                  </div>
                  <div className="text-sm font-bold text-slate-900">Annual Family Income</div>
                  
                  <div className="mt-3 space-y-2 text-xs">
                    <div>
                      <div className="font-semibold text-slate-700 flex items-center gap-1">💡 What does this mean?</div>
                      <p className="text-slate-600 text-[11px] mt-0.5">Total gross income earned by all family members in one financial year.</p>
                    </div>
                    <div>
                      <div className="font-semibold text-slate-700 flex items-center gap-1">✏️ What should you enter?</div>
                      <p className="text-slate-600 text-[11px] mt-0.5">Sum of father & mother salary matching the Tehsildar certificate.</p>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-blue-100">
                  <button
                    onClick={onLaunchDemo}
                    className="w-full py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center justify-center gap-1.5 shadow-sm transition-all"
                  >
                    <SlidersHorizontal className="w-3.5 h-3.5" />
                    <span>Try "Help Me Fill This"</span>
                  </button>
                </div>
              </div>
            </div>

          </div>

        </div>

      </section>

      {/* How it Works Section */}
      <section className="py-16 bg-white border-y border-slate-200/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight font-['Plus_Jakarta_Sans']">
              {t.howItWorksTitle}
            </h2>
            <p className="text-slate-500 text-sm mt-2">
              Transforming bureaucratic anxiety into clear, confident form completion in 3 simple steps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="p-6 rounded-2xl bg-slate-50/70 border border-slate-200/80 hover:border-blue-300 transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-lg mb-4">
                01
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Upload Form</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                {t.step1Desc}
              </p>
            </div>

            {/* Step 2 */}
            <div className="p-6 rounded-2xl bg-slate-50/70 border border-slate-200/80 hover:border-blue-300 transition-all">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-lg mb-4">
                02
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Understand Every Field</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                {t.step2Desc}
              </p>
            </div>

            {/* Step 3 */}
            <div className="p-6 rounded-2xl bg-slate-50/70 border border-slate-200/80 hover:border-blue-300 transition-all">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-lg mb-4">
                03
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Fill With Help</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                {t.step3Desc}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="py-20 bg-slate-50/60">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold text-blue-600 uppercase tracking-widest">Capabilities</span>
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight font-['Plus_Jakarta_Sans'] mt-2">
              Everything You Need to Fill Forms Flawlessly
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
              <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
                <FileSearch className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-base mb-1.5">AI Form Analysis</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Extracts structured fields, requirements, sections, and detected types from multi-page PDFs or image scans.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
              <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
                <Eye className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-base mb-1.5">Highlight Any Field</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Click any line on your document to immediately reveal simple explanations, examples, and required statuses.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
              <div className="w-10 h-10 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center mb-4">
                <SlidersHorizontal className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-base mb-1.5">Help Me Fill This</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Conversational assistant that computes complicated values (like Annual Family Income from monthly parent incomes).
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
              <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
                <Languages className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-base mb-1.5">Multilingual Guidance</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Instant toggling between English, Hindi, and Marathi so language is never a barrier to opportunity.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-base mb-1.5">Smart Validation & Progress</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Checks format rules for phone, email, and dates, while tracking reviewed items before you submit.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
              <div className="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center mb-4">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-base mb-1.5">Sensitive Data Protection</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Highlights sensitive banking, Aadhaar, and identity inputs with cautionary review warnings.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* Privacy & Trust Section */}
      <section className="py-14 bg-white border-t border-slate-200/80">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="w-12 h-12 mx-auto rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">Privacy &amp; Security by Design</h3>
          <p className="text-sm text-slate-600 max-w-xl mx-auto leading-relaxed">
            Your uploaded forms are processed securely in temporary memory and never stored permanently or shared with third parties. FormEase does not collect passwords or private banking credentials.
          </p>
          <div className="mt-4 text-xs text-slate-400">
            FormEase assists understanding • Never substitutes for official legal guidelines
          </div>
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="py-16 bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-800 text-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-extrabold tracking-tight mb-4 font-['Plus_Jakarta_Sans']">
            Ready to understand your form?
          </h2>
          <p className="text-blue-100 text-base max-w-xl mx-auto mb-8">
            Upload your document or explore our preloaded scholarship demo form to experience instant clarity.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button
              onClick={onStartUpload}
              className="px-6 py-3 rounded-xl bg-white text-blue-700 font-bold text-sm shadow-md hover:bg-blue-50 transition-all cursor-pointer"
            >
              Analyze a Form
            </button>
            <button
              onClick={onLaunchDemo}
              className="px-6 py-3 rounded-xl bg-blue-900/60 hover:bg-blue-900/80 text-white font-semibold text-sm border border-blue-400/40 transition-all cursor-pointer"
            >
              Explore Demo Form
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 border-t border-slate-200 bg-slate-50 text-center text-xs text-slate-500">
        <div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-3">
          <div className="font-semibold text-slate-700">FormEase — Understand Any Form. Fill It With Confidence.</div>
          <div>Built for seamless document accessibility and confidence.</div>
        </div>
      </footer>

    </div>
  );
};
