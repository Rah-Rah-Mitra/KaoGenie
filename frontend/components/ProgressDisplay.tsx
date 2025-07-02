
import React from 'react';
import { CheckCircleIcon } from './icons/CheckCircleIcon';
import { XCircleIcon } from './icons/XCircleIcon';

interface ProgressDisplayProps {
  steps: { key: string; label: string }[];
  currentStepKey: string;
  currentStatus: string;
  completedSteps: Set<string>;
  logs: string[];
  error: string | null;
}

const ProgressDisplay: React.FC<ProgressDisplayProps> = ({ steps, currentStepKey, currentStatus, completedSteps, logs, error }) => {
  const currentStepIndex = steps.findIndex(s => s.key === currentStepKey);

  return (
    <div className="fixed inset-0 bg-slate-900 bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50 p-4 transition-opacity duration-300" role="dialog" aria-modal="true" aria-labelledby="progress-title">
      <div className="w-full max-w-2xl bg-white dark:bg-slate-800 rounded-lg shadow-xl flex flex-col max-h-[90vh]">
        <header className="p-4 border-b border-slate-200 dark:border-slate-700 flex-shrink-0">
          <h2 id="progress-title" className="text-lg font-semibold text-slate-800 dark:text-slate-100">Generating Exam...</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{error ? 'An error occurred.' : currentStatus}</p>
        </header>
        
        <div className="flex-grow p-6 overflow-y-auto space-y-6">
          <div className="flow-root">
            <ul role="list" className="-mb-8">
              {steps.map((step, stepIdx) => (
                <li key={step.key}>
                  <div className="relative pb-8">
                    {stepIdx !== steps.length - 1 ? (
                      <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-slate-200 dark:bg-slate-700" aria-hidden="true" />
                    ) : null}
                    <div className="relative flex items-center space-x-3">
                      <div>
                        {completedSteps.has(step.key) || stepIdx < currentStepIndex ? (
                           <span className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white dark:ring-slate-800">
                            <CheckCircleIcon className="h-5 w-5 text-white" />
                          </span>
                        ) : stepIdx === currentStepIndex && !error ? (
                           <span className="h-8 w-8 rounded-full bg-sky-500 flex items-center justify-center ring-8 ring-white dark:ring-slate-800">
                            <div className="h-5 w-5 text-white animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                           </span>
                        ) : error && stepIdx === currentStepIndex ? (
                           <span className="h-8 w-8 rounded-full bg-red-500 flex items-center justify-center ring-8 ring-white dark:ring-slate-800">
                             <XCircleIcon className="h-5 w-5 text-white" />
                           </span>
                        ) : (
                           <span className="h-8 w-8 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center ring-8 ring-white dark:ring-slate-800">
                              <div className="h-2 w-2 rounded-full bg-slate-500 dark:bg-slate-400"></div>
                           </span>
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className={`text-sm font-medium ${stepIdx <= currentStepIndex ? 'text-slate-800 dark:text-slate-100' : 'text-slate-500 dark:text-slate-400'}`}>
                          {step.label}
                        </p>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4">
                <div className="flex">
                    <div className="flex-shrink-0">
                        <XCircleIcon className="h-5 w-5 text-red-400" aria-hidden="true" />
                    </div>
                    <div className="ml-3">
                        <h3 className="text-sm font-medium text-red-800 dark:text-red-300">Error Details</h3>
                        <div className="mt-2 text-sm text-red-700 dark:text-red-400">
                            <p>{error}</p>
                        </div>
                    </div>
                </div>
            </div>
          )}

          {logs.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-slate-600 dark:text-slate-300 mb-2">Detailed Log</h3>
              <div className="max-h-40 overflow-y-auto bg-slate-100 dark:bg-slate-900 rounded p-3 text-xs text-slate-500 dark:text-slate-400 font-mono">
                {logs.map((log, i) => <pre key={i} className="whitespace-pre-wrap break-words">{`> ${log}`}</pre>)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProgressDisplay;
