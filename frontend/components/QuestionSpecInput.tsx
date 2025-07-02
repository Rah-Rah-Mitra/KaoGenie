import React from 'react';
import { QuestionSpec, QuestionSpecRow } from '../types';
import { QUESTION_TYPES } from '../constants';
import { TrashIcon } from './icons/TrashIcon';

interface QuestionSpecInputProps {
  spec: QuestionSpecRow;
  index: number;
  onUpdate: <K extends keyof QuestionSpec>(index: number, field: K, value: QuestionSpec[K]) => void;
  onRemove: (index: number) => void;
  isRemovable: boolean;
}

const QuestionSpecInput: React.FC<QuestionSpecInputProps> = ({ spec, index, onUpdate, onRemove, isRemovable }) => {
  return (
    <div className="p-4 border border-slate-200 dark:border-slate-600 rounded-md space-y-3 bg-slate-50 dark:bg-slate-700 relative">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor={`qs-type-${spec.localId}`} className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Type</label>
          <select
            id={`qs-type-${spec.localId}`}
            value={spec.question_type}
            onChange={(e) => onUpdate(index, 'question_type', e.target.value)}
            className="w-full px-2 py-1.5 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-600 dark:border-slate-500 dark:text-slate-200"
          >
            {QUESTION_TYPES.map(type => (
              <option key={type} value={type} className="dark:bg-slate-600 dark:text-slate-200">{type}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor={`qs-count-${spec.localId}`} className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Count</label>
          <input
            type="number"
            id={`qs-count-${spec.localId}`}
            value={spec.count}
            min="1"
            onChange={(e) => onUpdate(index, 'count', parseInt(e.target.value, 10) || 1)}
            className="w-full px-2 py-1.5 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-600 dark:border-slate-500 dark:text-slate-200"
          />
        </div>
      </div>
      <div>
        <label htmlFor={`qs-prompt-${spec.localId}`} className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Optional Prompt/Guidance</label>
        <input
          type="text"
          id={`qs-prompt-${spec.localId}`}
          value={spec.prompt || ''}
          onChange={(e) => onUpdate(index, 'prompt', e.target.value)}
          placeholder="e.g., Focus on definitions"
          className="w-full px-2 py-1.5 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-600 dark:border-slate-500 dark:text-slate-200 dark:placeholder-slate-400"
        />
      </div>
      {isRemovable && (
        <button
          type="button"
          onClick={() => onRemove(index)}
          className="absolute top-2 right-2 p-1.5 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-100 dark:hover:bg-red-700/50 rounded-full transition-colors"
          aria-label="Remove specification"
        >
          <TrashIcon className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

export default QuestionSpecInput;