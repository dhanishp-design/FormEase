import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  AlertCircle,
  X,
  Sparkles,
  ArrowRight
} from 'lucide-react';

interface UploadDropzoneProps {
  onFileSelected: (file: File) => void;
  onLaunchDemo: () => void;
  onCancel?: () => void;
}

const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15MB

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({
  onFileSelected,
  onLaunchDemo,
}) => {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndHandleFile = (file: File) => {
    setErrorMessage(null);

    // Validate size
    if (file.size === 0) {
      setErrorMessage("The uploaded file is empty. Please upload a valid document.");
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setErrorMessage("File exceeds maximum size limit of 15MB. Please upload a smaller file.");
      return;
    }

    // Validate type
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    const isImage = file.type.startsWith('image/') || /\.(jpg|jpeg|png|webp|jfif|bmp|tiff)$/i.test(file.name);

    if (!isPdf && !isImage) {
      setErrorMessage("This file type isn't supported. Please upload PDF, JPG, JPEG, PNG, or WEBP.");
      return;
    }

    setSelectedFile(file);

    // Create preview if image
    if (isImage) {
      try {
        const objectUrl = URL.createObjectURL(file);
        setFilePreview(objectUrl);
      } catch {
        const reader = new FileReader();
        reader.onload = (e) => {
          setFilePreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);
      }
    } else {
      setFilePreview(null);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndHandleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndHandleFile(e.target.files[0]);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setFilePreview(null);
    setErrorMessage(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const startAnalysis = () => {
    if (selectedFile) {
      onFileSelected(selectedFile);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      
      <div className="text-center mb-8">
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight font-['Plus_Jakarta_Sans']">
          Upload your form
        </h2>
        <p className="text-slate-600 text-sm mt-1">
          Upload any form to detect fields and understand instructions in plain language.
        </p>
      </div>

      {/* Main Drag-and-drop Card */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-8 transition-all text-center ${
          dragActive
            ? 'border-blue-500 bg-blue-50/50 scale-[1.01]'
            : selectedFile
            ? 'border-emerald-300 bg-emerald-50/20'
            : 'border-slate-300 hover:border-blue-400 bg-white'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png,.webp,.jfif,.bmp,.tiff"
          onChange={handleChange}
          className="hidden"
          id="file-upload-input"
        />

        {!selectedFile ? (
          <div>
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-inner">
              <UploadCloud className="w-8 h-8 stroke-[2]" />
            </div>

            <h3 className="text-base font-bold text-slate-800 mb-1">
              Drag &amp; drop your PDF or image here
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              or browse from your device
            </p>

            <label
              htmlFor="file-upload-input"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-md shadow-blue-500/20 transition-all cursor-pointer"
            >
              Choose File
            </label>

            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-center gap-6 text-[11px] text-slate-400">
              <span>Supported: PDF, JPG, JPEG, PNG</span>
              <span>•</span>
              <span>Max: 15MB</span>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            
            {/* File Selected Preview Pill */}
            <div className="relative inline-block max-w-full">
              <div className="flex items-center gap-3 p-3 rounded-xl bg-white border border-slate-200 shadow-sm text-left">
                {filePreview ? (
                  <img
                    src={filePreview}
                    alt="Preview"
                    className="w-12 h-12 object-cover rounded-lg border border-slate-200"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs uppercase">
                    PDF
                  </div>
                )}

                <div className="overflow-hidden">
                  <div className="font-semibold text-slate-800 text-xs truncate max-w-xs">
                    {selectedFile.name}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • Ready for AI analysis
                  </div>
                </div>

                <button
                  onClick={removeFile}
                  className="p-1 rounded-full text-slate-400 hover:text-rose-600 hover:bg-slate-100 ml-2"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Analysis CTA */}
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={startAnalysis}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-md shadow-blue-500/25 transition-all cursor-pointer"
              >
                <span>Analyze Document</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={removeFile}
                className="px-4 py-3 rounded-xl text-slate-600 hover:bg-slate-100 text-xs font-semibold transition-all cursor-pointer"
              >
                Choose another file
              </button>
            </div>

          </div>
        )}

      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="mt-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
          <div>
            <div className="font-semibold">Unable to process document</div>
            <div className="mt-0.5 text-rose-700">{errorMessage}</div>
          </div>
        </div>
      )}

      {/* Demo Option Box */}
      <div className="mt-8 p-4 rounded-xl bg-gradient-to-r from-blue-50/70 to-indigo-50/70 border border-blue-200/70 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 text-left">
          <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900">Don't have a form handy?</div>
            <div className="text-[11px] text-slate-600">Explore our verified Scholarship Application demo with 12 real fields.</div>
          </div>
        </div>

        <button
          onClick={onLaunchDemo}
          className="w-full sm:w-auto px-4 py-2 rounded-lg bg-white hover:bg-blue-50 text-blue-700 border border-blue-200 font-semibold text-xs transition-all shadow-xs cursor-pointer whitespace-nowrap"
        >
          Try Demo Form
        </button>
      </div>

    </div>
  );
};
