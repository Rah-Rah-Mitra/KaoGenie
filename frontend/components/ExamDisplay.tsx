import React, { useState } from 'react';
import { FullExam, ExamQuestion } from '../types';
import MarkdownRenderer from './MarkdownRenderer';
import { RefreshIcon } from './icons/RefreshIcon';
import LoadingSpinner from './LoadingSpinner';

interface ExamDisplayProps {
  exam: FullExam;
  onRegenerate: (examId: string, questionId: string) => Promise<void>;
  isRegeneratingQuestionId: string | null;
  onBackToForms: () => void;
}

type ActiveTab = 'examPaper' | 'answerKey' | 'details';

const ExamDisplay: React.FC<ExamDisplayProps> = ({ exam, onRegenerate, isRegeneratingQuestionId, onBackToForms }) => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('examPaper');

  const renderOptionLetter = (index: number) => String.fromCharCode(65 + index);

  return (
    <div className="bg-white dark:bg-slate-800 p-6 md:p-8 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl md:text-3xl font-bold text-sky-700 dark:text-sky-400">{exam.exam_title}</h2>
        <button
          onClick={onBackToForms}
          className="text-sm bg-slate-200 hover:bg-slate-300 text-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600 dark:text-slate-300 font-semibold py-2 px-4 rounded-md transition-colors"
        >
          Create New Exam
        </button>
      </div>
      
      <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Exam ID: {exam.exam_id}</p>

      <div className="mb-6 border-b border-slate-300 dark:border-slate-600">
        <nav className="-mb-px flex space-x-4" aria-label="Tabs">
          {(['examPaper', 'answerKey', 'details'] as ActiveTab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeTab === tab 
                  ? 'border-sky-500 text-sky-600 dark:border-sky-400 dark:text-sky-400' 
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:border-slate-500'
                }`}
            >
              {tab === 'examPaper' ? 'Exam Paper' : tab === 'answerKey' ? 'Answer Key' : 'Generation Details'}
            </button>
          ))}
        </nav>
      </div>

      {activeTab === 'examPaper' && (
        <div className="prose prose-slate dark:prose-invert max-w-none">
          <MarkdownRenderer markdown={exam.exam_paper_markdown} />
        </div>
      )}

      {activeTab === 'answerKey' && (
        <div className="prose prose-slate dark:prose-invert max-w-none">
          <MarkdownRenderer markdown={exam.answer_key_markdown} />
        </div>
      )}

      {activeTab === 'details' && (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold text-slate-800 dark:text-slate-100 mb-2">Ingestion Summary</h3>
            <div className="bg-slate-50 dark:bg-slate-700 p-4 rounded-md text-sm space-y-1 text-slate-700 dark:text-slate-300">
              <p><strong>Message:</strong> {exam.ingestion_summary.message}</p>
              <p><strong>Processed Sources:</strong> {exam.ingestion_summary.processed_sources_count}</p>
              <p><strong>Total Chunks Ingested:</strong> {exam.ingestion_summary.total_chunks_ingested}</p>
              <p><strong>Collections Created:</strong> {exam.ingestion_summary.collections_created.join(', ') || 'None'}</p>
            </div>
          </div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800 dark:text-slate-100 mb-2">Sources Used ({exam.sources_used.length})</h3>
            {exam.sources_used.length > 0 ? (
              <ul className="list-disc list-inside bg-slate-50 dark:bg-slate-700 p-4 rounded-md text-sm max-h-60 overflow-y-auto text-slate-700 dark:text-slate-300">
                {exam.sources_used.map((source, idx) => (
                  <li key={idx} className="truncate hover:whitespace-normal">
                    <a href={source} target="_blank" rel="noopener noreferrer" className="text-sky-600 dark:text-sky-400 hover:underline">{source}</a>
                  </li>
                ))}
              </ul>
            ) : <p className="text-sm text-slate-500 dark:text-slate-400">No specific sources were listed for this exam generation.</p>}
          </div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800 dark:text-slate-100 mb-3">Generated Questions ({exam.questions.length})</h3>
            <div className="space-y-4">
              {exam.questions.map((q, index) => (
                <div key={q.id} className="p-4 border border-slate-200 dark:border-slate-600 rounded-md bg-slate-50/50 dark:bg-slate-700/50">
                  <div className="flex justify-between items-start">
                    <h4 className="font-semibold text-slate-700 dark:text-slate-200">Question {index + 1} ({q.question_type})</h4>
                    <button
                      onClick={() => onRegenerate(exam.exam_id, q.id)}
                      disabled={isRegeneratingQuestionId === q.id}
                      className="flex items-center text-xs text-sky-600 hover:text-sky-800 dark:text-sky-400 dark:hover:text-sky-300 font-medium py-1 px-2 rounded-md border border-sky-300 dark:border-sky-500 hover:bg-sky-50 dark:hover:bg-sky-700 transition-colors disabled:opacity-50 disabled:cursor-wait"
                      title="Regenerate this question"
                    >
                      {isRegeneratingQuestionId === q.id ? (
                        <LoadingSpinner size="small" />
                      ) : (
                        <RefreshIcon className="w-3.5 h-3.5 mr-1" />
                      )}
                      Regenerate
                    </button>
                  </div>
                  <p className="mt-1 text-sm text-slate-600 dark:text-slate-300 whitespace-pre-wrap">{q.question_text}</p>
                  {q.image_url && (
                    <img src={q.image_url} alt="Question related" className="mt-2 max-w-xs max-h-48 rounded border border-slate-300 dark:border-slate-600" />
                  )}
                  {q.options && q.options.length > 0 && (
                    <ul className="mt-2 space-y-1 text-sm">
                      {q.options.map((opt, optIdx) => (
                        <li key={optIdx} className="text-slate-500 dark:text-slate-400">
                          {renderOptionLetter(optIdx)}. {opt}
                        </li>
                      ))}
                    </ul>
                  )}
                  <details className="mt-3 text-xs">
                    <summary className="cursor-pointer text-sky-700 dark:text-sky-400 font-medium">Show Solution Details</summary>
                    <div className="mt-1 p-2 bg-white dark:bg-slate-800/70 border border-slate-200 dark:border-slate-600 rounded text-slate-600 dark:text-slate-300 space-y-1">
                      <p><strong>Explanation:</strong> <span className="whitespace-pre-wrap">{q.solution.explanation}</span></p>
                      {q.solution.final_answer && <p><strong>Final Answer:</strong> {q.solution.final_answer}</p>}
                      {q.solution.correct_option_index !== null && q.solution.correct_option_index !== undefined && q.options && (
                        <p><strong>Correct Option:</strong> {renderOptionLetter(q.solution.correct_option_index)}. {q.options[q.solution.correct_option_index]}</p>
                      )}
                    </div>
                  </details>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExamDisplay;