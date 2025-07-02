
import React, { useState } from 'react';

interface ExamFormFileProps {
  onSubmit: (formData: FormData) => void;
  isLoading: boolean;
}

const ExamFormFile: React.FC<ExamFormFileProps> = ({ onSubmit, isLoading }) => {
  const [examTitle, setExamTitle] = useState<string>('');
  const [subject, setSubject] = useState<string>('');
  const [gradeLevel, setGradeLevel] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      alert("Please upload a source document file.");
      return;
    }

    const formData = new FormData();
    formData.append('exam_title', examTitle);
    formData.append('subject', subject);
    formData.append('grade_level', gradeLevel);
    formData.append('example_paper', file);
    
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-slate-800 p-6 md:p-8 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700">
      <div>
        <label htmlFor="examTitleFile" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Exam Title</label>
        <input
          type="text"
          id="examTitleFile"
          value={examTitle}
          onChange={(e) => setExamTitle(e.target.value)}
          required
          className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200 dark:placeholder-slate-400"
          placeholder="e.g., Final Exam Based on Uploaded Syllabus"
        />
      </div>
       <div>
        <label htmlFor="subjectFile" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Subject</label>
        <input
          type="text"
          id="subjectFile"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          required
          className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200 dark:placeholder-slate-400"
          placeholder="e.g., English Literature, Biology"
        />
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Provide a subject to help the AI categorize the content.</p>
      </div>
      <div>
        <label htmlFor="gradeLevelFile" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Grade Level</label>
        <input
          type="text"
          id="gradeLevelFile"
          value={gradeLevel}
          onChange={(e) => setGradeLevel(e.target.value)}
          required
          className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500 sm:text-sm text-slate-700 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200 dark:placeholder-slate-400"
          placeholder="e.g., High School, University"
        />
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Provide a grade level to help the AI set the difficulty.</p>
      </div>
      <div>
        <label htmlFor="fileUpload" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Source Document (PDF, DOCX, TXT, etc.)</label>
        <input
          type="file"
          id="fileUpload"
          onChange={handleFileChange}
          required
          className="w-full text-sm text-slate-700 dark:text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 dark:file:bg-sky-700 dark:file:text-sky-200 dark:hover:file:bg-sky-600"
        />
         {file && <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Selected: {file.name}</p>}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-sky-600 hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-600 text-white font-semibold py-2.5 px-4 rounded-md shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Generating Exam...' : 'Generate Exam from File'}
      </button>
    </form>
  );
};

export default ExamFormFile;
