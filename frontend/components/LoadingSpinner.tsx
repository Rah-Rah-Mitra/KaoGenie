import React from 'react';

interface LoadingSpinnerProps {
  overlay?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ overlay = false, size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-5 h-5 border-2',
    medium: 'w-8 h-8 border-4',
    large: 'w-12 h-12 border-[6px]',
  };

  const spinner = (
    <div className={`animate-spin rounded-full ${sizeClasses[size]} border-sky-500 dark:border-sky-400 border-t-transparent`}></div>
  );

  if (overlay) {
    return (
      <div className="fixed inset-0 bg-slate-900 bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50">
        <div className="p-4 bg-white dark:bg-slate-800 rounded-lg shadow-xl flex flex-col items-center space-y-2">
          {spinner}
          <p className="text-sm text-slate-600 dark:text-slate-300">Loading...</p>
        </div>
      </div>
    );
  }

  return spinner;
};

export default LoadingSpinner;