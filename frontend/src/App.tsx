import React, { useState, useEffect } from 'react';
import type { FormAnalysisData, FormField, Language } from './types';
import { analyzeDocument, checkBackendHealth } from './services/api';
import { Navbar } from './components/Navbar';
import { LandingPage } from './components/LandingPage';
import { UploadDropzone } from './components/UploadDropzone';
import { AnalysisProgress } from './components/AnalysisProgress';
import { FormAnalyzer } from './components/FormAnalyzer';
import { AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [view, setView] = useState<'landing' | 'upload' | 'analyzing' | 'workspace'>('landing');
  const [language, setLanguage] = useState<Language>('en');
  const [formData, setFormData] = useState<FormAnalysisData | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);

  useEffect(() => {
    // Proactively check backend connection
    checkBackendHealth();
  }, []);

  const [animationCompleted, setAnimationCompleted] = useState<boolean>(false);

  // Automatically transition to workspace as soon as animation has reached completion AND formData is ready
  useEffect(() => {
    if (view === 'analyzing' && animationCompleted && formData) {
      setView('workspace');
    }
  }, [view, animationCompleted, formData]);

  const handleLaunchDemo = async () => {
    setError(null);
    setIsDemoMode(true);
    setUploadedFile(null);
    setFormData(null);
    setAnimationCompleted(false);
    setView('analyzing');

    try {
      const data = await analyzeDocument(null, true, language);
      setFormData(data);
    } catch (err: any) {
      console.error('Demo load error:', err);
      setError('Unable to load demo form. Please try again.');
      setView('landing');
    }
  };

  const handleFileSelected = async (file: File) => {
    setError(null);
    setIsDemoMode(false);
    setUploadedFile(file);
    setFormData(null);
    setAnimationCompleted(false);
    setView('analyzing');

    try {
      const data = await analyzeDocument(file, false, language);
      
      // If uploaded file is an image, set instant local object URL preview
      let previewUrl = data.document_preview_url;
      const isImg = file.type.startsWith('image/') || /\.(jpe?g|png|webp|gif|bmp|jfif|tiff?)$/i.test(file.name);
      if (isImg) {
        try {
          previewUrl = URL.createObjectURL(file);
        } catch {
          // fallback to data.document_preview_url
        }
      }
      setFormData({
        ...data,
        document_preview_url: previewUrl || data.document_preview_url,
      });
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(err.message || 'We could not clearly read this form. Try uploading a clearer image or PDF.');
      setView('upload');
    }
  };

  const handleAnalysisCompleted = () => {
    setAnimationCompleted(true);
    if (formData) {
      setView('workspace');
    }
  };

  const handleReset = () => {
    setFormData(null);
    setUploadedFile(null);
    setError(null);
    setIsDemoMode(false);
    setView('landing');
  };

  const handleLanguageChange = async (newLang: Language) => {
    setLanguage(newLang);
    if (formData) {
      // Re-fetch localized analysis data
      try {
        const refreshed = await analyzeDocument(uploadedFile, isDemoMode, newLang);
        // Retain user filled values and reviewed flags
        const mergedFields = refreshed.fields.map((f) => {
          const prev = formData.fields.find((p) => p.id === f.id);
          return {
            ...f,
            user_value: prev?.user_value,
            is_reviewed: prev?.is_reviewed,
          };
        });
        setFormData({
          ...refreshed,
          fields: mergedFields,
          document_preview_url: formData.document_preview_url || refreshed.document_preview_url,
        });
      } catch (err) {
        console.error('Language switch refresh error:', err);
      }
    }
  };

  const handleUpdateField = (fieldId: string, updates: Partial<FormField>) => {
    if (!formData) return;
    const updatedFields = formData.fields.map((f) =>
      f.id === fieldId ? { ...f, ...updates } : f
    );
    setFormData({
      ...formData,
      fields: updatedFields,
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 font-sans text-slate-900">
      
      {/* Global Navbar */}
      <Navbar
        currentLanguage={language}
        onLanguageChange={handleLanguageChange}
        onReset={handleReset}
        onLaunchDemo={handleLaunchDemo}
        isDemoMode={isDemoMode}
        isInWorkspace={view === 'workspace'}
      />

      {/* Global Error Banner if any */}
      {error && (
        <div className="bg-rose-50 border-b border-rose-200 px-4 py-3 text-xs text-rose-800 flex items-center justify-between">
          <div className="flex items-center gap-2 max-w-4xl mx-auto w-full">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span className="font-medium">{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-rose-500 hover:text-rose-800 font-bold ml-2 text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main View Router */}
      <main className="flex-1 flex flex-col">
        {view === 'landing' && (
          <LandingPage
            onStartUpload={() => setView('upload')}
            onLaunchDemo={handleLaunchDemo}
            language={language}
          />
        )}

        {view === 'upload' && (
          <div className="py-12">
            <UploadDropzone
              onFileSelected={handleFileSelected}
              onLaunchDemo={handleLaunchDemo}
              onCancel={() => setView('landing')}
            />
          </div>
        )}

        {view === 'analyzing' && (
          <AnalysisProgress
            formTitle={formData?.form_title}
            totalFields={formData?.fields?.length || 12}
            isDataReady={Boolean(formData)}
            onComplete={handleAnalysisCompleted}
          />
        )}

        {view === 'workspace' && formData && (
          <FormAnalyzer
            formData={formData}
            language={language}
            onUpdateField={handleUpdateField}
            onLanguageChange={handleLanguageChange}
          />
        )}
      </main>

    </div>
  );
};

export default App;
