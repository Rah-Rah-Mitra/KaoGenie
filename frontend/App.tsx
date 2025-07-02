
import React, { useState, useCallback } from 'react';
import { ExamFromTopicRequest, FullExam } from './types';
import { generateExamFromTopic, generateExamFromFile, regenerateSingleQuestion, StreamCallbacks } from './services/apiService';
import Layout from './components/Layout';
import ExamFormTopic from './components/ExamFormTopic';
import ExamFormFile from './components/ExamFormFile';
import ExamDisplay from './components/ExamDisplay';
import ProgressDisplay from './components/ProgressDisplay';
import ErrorAlert from './components/ErrorAlert';
import ThemeToggle from './components/ThemeToggle';

type ViewMode = 'formTopic' | 'formFile' | 'examView';

const TOPIC_STEPS = [
    { key: 'start_ingestion', label: 'Starting Data Ingestion' },
    { key: 'text_query_gen', label: 'Generating Search Queries' },
    { key: 'web_search', label: 'Searching the Web' },
    { key: 'crawling', label: 'Analyzing Search Results' },
    { key: 'text_processing', label: 'Processing Text Content' },
    { key: 'image_query_gen', label: 'Generating Image Queries' },
    { key: 'image_search', label: 'Searching for Images' },
    { key: 'image_processing', label: 'Processing Images' },
    { key: 'question_generation', label: 'Generating Exam Questions' },
    { key: 'solution_generation', label: 'Generating Solutions & Answers' },
    { key: 'compilation', label: 'Compiling Final Exam Documents' },
];

const FILE_STEPS = [
    { key: 'file_processing', label: 'Processing Uploaded File' },
    { key: 'spec_generation', label: 'Analyzing File to Create Exam Structure' },
    { key: 'question_generation', label: 'Generating Exam Questions' },
    { key: 'solution_generation', label: 'Generating Solutions & Answers' },
    { key: 'compilation', label: 'Compiling Final Exam Documents' },
];

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewMode>('formTopic');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [examData, setExamData] = useState<FullExam | null>(null);
  const [regeneratingQuestionId, setRegeneratingQuestionId] = useState<string | null>(null);

  // State for streaming progress
  const [progressSteps, setProgressSteps] = useState(TOPIC_STEPS);
  const [progressStepKey, setProgressStepKey] = useState<string>('');
  const [progressStatus, setProgressStatus] = useState<string>('');
  const [progressLogs, setProgressLogs] = useState<string[]>([]);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());
  const [progressError, setProgressError] = useState<string | null>(null);

  const resetProgress = () => {
    setProgressStepKey('');
    setProgressStatus('Initializing...');
    setProgressLogs([]);
    setCompletedSteps(new Set());
    setProgressError(null);
    setError(null);
  };

  const handleStreamedGeneration = useCallback(async (
    apiCall: (callbacks: StreamCallbacks) => Promise<void>,
    steps: {key: string, label: string}[]
  ) => {
    resetProgress();
    setProgressSteps(steps);
    setIsLoading(true);
    setExamData(null);

    let finalResultReceived = false;

    const callbacks: StreamCallbacks = {
      onProgress: (progress) => {
        setProgressStepKey(prevKey => {
            if (prevKey && progress.step !== prevKey) {
                setCompletedSteps(prevCompleted => new Set(prevCompleted).add(prevKey));
            }
            return progress.step;
        });
        setProgressStatus(progress.status);
      },
      onLog: (log) => {
        setProgressLogs(prev => [...prev, log.message]);
      },
      onResult: (result) => {
        finalResultReceived = true;
        setExamData(result);
        setCurrentView('examView');
      },
      onError: (err) => {
        setProgressError(err.detail || 'An unknown streaming error occurred.');
      },
      onEnd: () => {
        setIsLoading(false);
        // Use functional state update to get the latest progressError
        setProgressError(currentProgressError => {
            if (currentProgressError) {
                setError(currentProgressError);
            } else if (!finalResultReceived) {
                setError("The generation process finished unexpectedly without a result. Please try again.");
            }
            return currentProgressError; 
        });
      },
    };

    try {
      await apiCall(callbacks);
    } catch (err: any) {
      setError(err.message || 'An unknown error occurred.');
      setIsLoading(false);
    }
  }, []);

  const handleGenerateFromTopic = useCallback(async (data: ExamFromTopicRequest) => {
    await handleStreamedGeneration((callbacks) => generateExamFromTopic(data, callbacks), TOPIC_STEPS);
  }, [handleStreamedGeneration]);

  const handleGenerateFromFile = useCallback(async (formData: FormData) => {
    await handleStreamedGeneration((callbacks) => generateExamFromFile(formData, callbacks), FILE_STEPS);
  }, [handleStreamedGeneration]);

  const handleRegenerateQuestion = useCallback(async (examId: string, questionId: string) => {
    if (!examData) return;
    setRegeneratingQuestionId(questionId);
    setError(null);
    try {
      const newQuestion = await regenerateSingleQuestion(examId, questionId);
      setExamData(prevExam => {
        if (!prevExam) return null;
        return {
          ...prevExam,
          questions: prevExam.questions.map(q => q.id === questionId ? newQuestion : q),
        };
      });
    } catch (err: any) {
      setError(`Failed to regenerate question ${questionId}: ${err.message || 'Unknown error'}`);
    } finally {
      setRegeneratingQuestionId(null);
    }
  }, [examData]);

  const navigateToForm = (formType: 'formTopic' | 'formFile') => {
    setCurrentView(formType);
    setExamData(null);
    setError(null);
  };

  return (
    <Layout>
      {isLoading && 
        <ProgressDisplay
          steps={progressSteps}
          currentStepKey={progressStepKey}
          currentStatus={progressStatus}
          completedSteps={completedSteps}
          logs={progressLogs}
          error={progressError}
        />
      }
      <div className="container mx-auto p-4 md:p-8 max-w-5xl">
        <header className="mb-8 text-center relative">
          <h1 className="text-4xl font-bold text-sky-700 dark:text-sky-400">AI Exam Generator</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2">Create customized exams effortlessly.</p>
          <div className="absolute top-0 right-0 p-1">
            <ThemeToggle />
          </div>
        </header>

        {error && !isLoading && <ErrorAlert message={error} onClose={() => setError(null)} />}

        {currentView !== 'examView' && (
          <div className="mb-6 flex justify-center space-x-2">
            <button
              onClick={() => navigateToForm('formTopic')}
              className={`px-6 py-2 rounded-md font-semibold transition-colors ${
                currentView === 'formTopic' 
                  ? 'bg-sky-600 text-white shadow-md dark:bg-sky-500' 
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'
              }`}
            >
              From Topic
            </button>
            <button
              onClick={() => navigateToForm('formFile')}
              className={`px-6 py-2 rounded-md font-semibold transition-colors ${
                currentView === 'formFile' 
                  ? 'bg-sky-600 text-white shadow-md dark:bg-sky-500' 
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'
              }`}
            >
              From File
            </button>
          </div>
        )}

        {currentView === 'formTopic' && (
          <ExamFormTopic onSubmit={handleGenerateFromTopic} isLoading={isLoading} />
        )}
        {currentView === 'formFile' && (
          <ExamFormFile onSubmit={handleGenerateFromFile} isLoading={isLoading} />
        )}
        {currentView === 'examView' && examData && (
          <ExamDisplay
            exam={examData}
            onRegenerate={handleRegenerateQuestion}
            isRegeneratingQuestionId={regeneratingQuestionId}
            onBackToForms={() => navigateToForm('formTopic')}
          />
        )}
      </div>
    </Layout>
  );
};

export default App;
