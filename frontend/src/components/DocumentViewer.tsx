import React, { useState, useRef } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import type { FormField } from '../types';

interface DocumentViewerProps {
  documentUrl?: string;
  fields: FormField[];
  selectedFieldId: string | null;
  onSelectField: (fieldId: string) => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentUrl = '/demo-form.svg',
  fields,
  selectedFieldId,
  onSelectField,
}) => {
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [showOverlays, setShowOverlays] = useState<boolean>(true);
  const [hoveredFieldId, setHoveredFieldId] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 15, 200));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 15, 60));
  const handleResetZoom = () => setZoomLevel(100);

  const selectedField = fields.find((f) => f.id === selectedFieldId);

  return (
    <div className="flex flex-col h-full bg-slate-100 rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
      
      {/* Document Controls Toolbar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-2.5 bg-white border-b border-slate-200 text-xs text-slate-600 gap-2 shrink-0">
        
        {/* Left: Document Info & active field */}
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-800">Form Document</span>
          <span className="text-slate-300">•</span>
          <span className="text-[11px] text-slate-500">Page 1 of 1</span>
          
          {selectedField && (
            <span className="hidden sm:inline-flex items-center gap-1 ml-2 px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 font-semibold border border-blue-200/60 text-[11px]">
              <Sparkles className="w-3 h-3" />
              <span>{selectedField.name}</span>
            </span>
          )}
        </div>

        {/* Right: Zoom and Overlay Controls */}
        <div className="flex items-center gap-1.5">
          
          {/* Overlay Toggle */}
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg font-medium transition-all ${
              showOverlays
                ? 'bg-blue-50 text-blue-700 border border-blue-200'
                : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
            }`}
            title="Toggle interactive field highlight boxes"
          >
            <Layers className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Highlights</span>
          </button>

          <div className="h-4 w-px bg-slate-200 mx-1" />

          {/* Zoom Buttons */}
          <button
            onClick={handleZoomOut}
            disabled={zoomLevel <= 60}
            className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 disabled:opacity-40 transition-all cursor-pointer"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>

          <span className="text-[11px] font-mono font-medium text-slate-600 px-1 w-11 text-center">
            {zoomLevel}%
          </span>

          <button
            onClick={handleZoomIn}
            disabled={zoomLevel >= 200}
            className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 disabled:opacity-40 transition-all cursor-pointer"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>

          <button
            onClick={handleResetZoom}
            className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 transition-all cursor-pointer"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

        </div>

      </div>

      {/* Main Document Scrollport */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-4 flex justify-center items-start min-h-[500px] relative select-none"
      >
        <div
          className="relative bg-white shadow-lg shadow-slate-300/40 rounded-lg transition-transform duration-150 origin-top"
          style={{
            width: `${Math.round(760 * (zoomLevel / 100))}px`,
            maxWidth: 'none',
          }}
        >
          {/* Base Document (SVG or Image) */}
          <img
            src={documentUrl}
            alt="Application Form Preview"
            className="w-full h-auto block rounded-lg pointer-events-none"
          />

          {/* Interactive Bounding Box Highlights */}
          {showOverlays &&
            fields.map((field) => {
              if (!field.bbox) return null;
              const isSelected = field.id === selectedFieldId;
              const isHovered = field.id === hoveredFieldId;

              // Ensure bounding box values are valid percentages (0-100)
              const rawX = field.bbox.x > 100 ? field.bbox.x / 10 : field.bbox.x;
              const rawY = field.bbox.y > 100 ? field.bbox.y / 10 : field.bbox.y;
              const rawW = field.bbox.width > 100 ? field.bbox.width / 10 : field.bbox.width;
              const rawH = field.bbox.height > 100 ? field.bbox.height / 10 : field.bbox.height;

              const boxX = Math.max(0, Math.min(95, rawX));
              const boxY = Math.max(0, Math.min(98, rawY));
              const boxW = Math.max(2, Math.min(100 - boxX, rawW));
              const boxH = Math.max(1.5, Math.min(100 - boxY, rawH));

              return (
                <div
                  key={field.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectField(field.id);
                  }}
                  onMouseEnter={() => setHoveredFieldId(field.id)}
                  onMouseLeave={() => setHoveredFieldId(null)}
                  className={`absolute rounded-md cursor-pointer transition-all duration-150 z-10 ${
                    isSelected
                      ? 'border-2 border-blue-600 bg-blue-500/25 ring-4 ring-blue-500/20 shadow-md'
                      : isHovered
                      ? 'border-2 border-indigo-400 bg-indigo-500/15 ring-2 ring-indigo-400/20'
                      : 'border border-blue-400/40 hover:border-blue-500 bg-blue-500/5 hover:bg-blue-500/15'
                  }`}
                  style={{
                    left: `${boxX}%`,
                    top: `${boxY}%`,
                    width: `${boxW}%`,
                    height: `${boxH}%`,
                  }}
                >
                  {/* Field Badge on Active / Hover */}
                  {(isSelected || isHovered) && (
                    <div
                      className={`absolute -top-6 left-0 px-2 py-0.5 rounded text-[10px] font-bold shadow-md whitespace-nowrap z-20 flex items-center gap-1 ${
                        isSelected
                          ? 'bg-blue-600 text-white'
                          : 'bg-indigo-600 text-white'
                      }`}
                    >
                      <span>{field.name}</span>
                      {field.required && <span className="text-red-300">*</span>}
                    </div>
                  )}

                  {/* Sensitive indicator pill */}
                  {field.sensitive && !isSelected && (
                    <div className="absolute top-1 right-1 w-2 h-2 rounded-full bg-rose-500" title="Sensitive Field" />
                  )}
                </div>
              );
            })}
        </div>
      </div>

      {/* Bottom Hint */}
      <div className="px-4 py-2 bg-white/80 border-t border-slate-200 text-[11px] text-slate-500 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-blue-600" />
          <span>Click any highlighted field on the form to view plain-language explanation &amp; smart fill guidance.</span>
        </div>
        <div className="hidden md:block font-mono text-[10px] text-slate-400">
          Scroll to view full form
        </div>
      </div>

    </div>
  );
};
