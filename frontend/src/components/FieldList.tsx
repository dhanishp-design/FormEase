import React, { useState } from 'react';
import {
  CheckCircle2,
  Search
} from 'lucide-react';
import type { FormField } from '../types';

interface FieldListProps {
  fields: FormField[];
  selectedFieldId: string | null;
  onSelectField: (fieldId: string) => void;
}

export const FieldList: React.FC<FieldListProps> = ({
  fields,
  selectedFieldId,
  onSelectField,
}) => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filterType, setFilterType] = useState<'all' | 'required' | 'reviewed'>('all');

  const filteredFields = fields.filter((f) => {
    const matchesSearch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          f.section.toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchesSearch) return false;

    if (filterType === 'required') return f.required;
    if (filterType === 'reviewed') return Boolean(f.is_reviewed);
    return true;
  });

  // Group by section
  const sections: { [sectionName: string]: FormField[] } = {};
  filteredFields.forEach((field) => {
    if (!sections[field.section]) {
      sections[field.section] = [];
    }
    sections[field.section].push(field);
  });

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
      
      {/* Header & Search */}
      <div className="p-3.5 border-b border-slate-100 bg-slate-50/50 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Detected Fields ({fields.length})
          </div>
          <div className="flex gap-1 text-[11px]">
            <button
              onClick={() => setFilterType('all')}
              className={`px-2 py-0.5 rounded font-medium ${
                filterType === 'all'
                  ? 'bg-slate-200 text-slate-800'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType('required')}
              className={`px-2 py-0.5 rounded font-medium ${
                filterType === 'required'
                  ? 'bg-red-100 text-red-700 font-bold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Required
            </button>
            <button
              onClick={() => setFilterType('reviewed')}
              className={`px-2 py-0.5 rounded font-medium ${
                filterType === 'reviewed'
                  ? 'bg-emerald-100 text-emerald-800 font-bold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Reviewed
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search fields..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Field List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-3">
        {Object.entries(sections).map(([sectionTitle, sectionFields]) => (
          <div key={sectionTitle}>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 py-1">
              {sectionTitle}
            </div>

            <div className="space-y-1">
              {sectionFields.map((field) => {
                const isSelected = field.id === selectedFieldId;

                return (
                  <button
                    key={field.id}
                    onClick={() => onSelectField(field.id)}
                    className={`w-full text-left p-2.5 rounded-xl transition-all flex items-center justify-between gap-2 cursor-pointer ${
                      isSelected
                        ? 'bg-blue-600 text-white shadow-sm ring-1 ring-blue-700'
                        : 'hover:bg-slate-50 text-slate-700 border border-transparent hover:border-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2 overflow-hidden">
                      {/* Status Icon */}
                      {field.is_reviewed ? (
                        <CheckCircle2
                          className={`w-4 h-4 shrink-0 ${
                            isSelected ? 'text-white' : 'text-emerald-600'
                          }`}
                        />
                      ) : (
                        <div
                          className={`w-2 h-2 rounded-full shrink-0 ${
                            field.required
                              ? isSelected ? 'bg-white' : 'bg-red-500'
                              : isSelected ? 'bg-blue-200' : 'bg-slate-300'
                          }`}
                        />
                      )}

                      {/* Field Name */}
                      <span className="text-xs font-semibold truncate">
                        {field.name}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0 text-[10px]">
                      {field.sensitive && (
                        <span
                          className={`px-1 py-0.5 rounded text-[9px] font-bold ${
                            isSelected
                              ? 'bg-blue-800 text-rose-200'
                              : 'bg-rose-50 text-rose-600 border border-rose-200'
                          }`}
                        >
                          Sensitive
                        </span>
                      )}

                      {field.required ? (
                        <span
                          className={`font-bold ${
                            isSelected ? 'text-red-200' : 'text-red-500'
                          }`}
                        >
                          *
                        </span>
                      ) : (
                        <span
                          className={`text-[9px] uppercase px-1 rounded ${
                            isSelected ? 'text-blue-200' : 'text-slate-400 bg-slate-100'
                          }`}
                        >
                          Opt
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        {filteredFields.length === 0 && (
          <div className="text-center py-8 text-xs text-slate-400">
            No fields found matching "{searchQuery}"
          </div>
        )}
      </div>

    </div>
  );
};
