import React, { useState, useCallback } from 'react';
import { ExamFromTopicRequest, QuestionSpec, QuestionSpecRow } from '../types';
import QuestionSpecInput from './QuestionSpecInput';
import { PlusIcon } from './icons/PlusIcon';

interface ExamFormTopicProps {
  onSubmit: (data: ExamFromTopicRequest) => void;
  isLoading: boolean;
}

const ExamFormTopic: React.FC<ExamFormTopicProps> = ({ onSubmit, isLoading }) => {
  const [subject, setSubject] = useState<string>('');
  const [gradeLevel, setGradeLevel] = useState<string>('');
  const [examTitle, setExamTitle] = useState<string>('');
  const [questionSpecs, setQuestionSpecs] = useState<QuestionSpecRow[]>([
    { localId: Date.now().toString(), question_type: 'MCQ', count: 5, prompt: '' }
  ]);

  const addQuestionSpec = useCallback(() => {
    setQuestionSpecs(prev => [
      ...prev,
      { localId: Date.now().toString(), question_type: 'MCQ', count: 1, prompt: '' }
    ]);
  }, []);

  const updateQuestionSpec = useCallback(<K extends keyof QuestionSpec>(index: number, field: K, value: QuestionSpec[K]) => {
    setQuestionSpecs(prev => 
      prev.map((spec, i) => (i === index ? { ...spec, [field]: value } : spec))
    );
  }, []);
  
  const removeQuestionSpec = useCallback((index: number) => {
    setQuestionSpecs(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (questionSpecs.length === 0) {
      alert("Please add at least one question specification.");
      return;
    }
    const finalSpecs: QuestionSpec[] = questionSpecs.map(({ localId, ...spec }) => spec);
    onSubmit({ subject, grade_level: gradeLevel, exam_title: examTitle, question_specs: finalSpecs });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-slate-800 p-6 md:p-8 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700">
      <div>
        <label htmlFor="subject" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Subject</label>
        <input
          type="text"
          id="subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          required
          className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200 dark:placeholder-slate-400"
          placeholder="e.g., Quantum Physics"
        />
      </div>
      <div>
        <label htmlFor="gradeLevel" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Grade Level</label>
        <input
          type="text"
          id="gradeLevel"
          value={gradeLevel}
          onChange={(e) => setGradeLevel(e.target.value)}
          required
          className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200 dark:placeholder-slate-400"
          placeholder="e.g., University Graduate"
        />
      </div>
      <div>
        <label htmlFor="examTitle" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Exam Title</label>
        <input
          type="text"
          id="examTitle"
          value={examTitle}
          onChange={(e) => setExamTitle(e.target.value)}
          required
          className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200 dark:placeholder-slate-400"
          placeholder="e.g., Midterm Exam: Quantum Mechanics I"
        />
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-medium text-slate-800 dark:text-slate-100">Question Specifications</h3>
        {questionSpecs.map((spec, index) => (
          <QuestionSpecInput
            key={spec.localId}
            spec={spec}
            index={index}
            onUpdate={updateQuestionSpec}
            onRemove={removeQuestionSpec}
            isRemovable={questionSpecs.length > 1}
          />
        ))}
        <button
          type="button"
          onClick={addQuestionSpec}
          className="flex items-center space-x-2 text-sm text-sky-600 hover:text-sky-800 dark:text-sky-400 dark:hover:text-sky-300 font-medium py-2 px-3 rounded-md border border-sky-300 dark:border-sky-600 hover:bg-sky-50 dark:hover:bg-sky-700 transition-colors"
        >
          <PlusIcon className="w-4 h-4" />
          <span>Add Question Specification</span>
        </button>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-sky-600 hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-600 text-white font-semibold py-2.5 px-4 rounded-md shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Generating Exam...' : 'Generate Exam from Topic'}
      </button>
    </form>
  );
};

export default ExamFormTopic;