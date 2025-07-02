import React from 'react';
import ReactMarkdown, { Options } from 'react-markdown'; // Updated import for Options/Components
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

interface MarkdownRendererProps {
  markdown: string;
}

// Define the components object with the explicit type from react-markdown
// Note: Using dark:prose-invert on the parent element in ExamDisplay.tsx handles most of the basic text color inversions.
// Specific overrides here are for elements with explicit backgrounds or borders.
const markdownComponents: Options['components'] = {
  h1: ({node, ...props}) => <h1 className="text-3xl font-bold my-4 pb-2 border-b border-slate-300 dark:border-slate-700" {...props} />,
  h2: ({node, ...props}) => <h2 className="text-2xl font-semibold my-3 pb-1 border-b border-slate-200 dark:border-slate-700" {...props} />,
  h3: ({node, ...props}) => <h3 className="text-xl font-semibold my-2" {...props} />,
  h4: ({node, ...props}) => <h4 className="text-lg font-semibold my-1" {...props} />,
  p: ({node, ...props}) => <p className="mb-3 leading-relaxed" {...props} />,
  ul: ({node, ...props}) => <ul className="list-disc list-inside mb-3 pl-4 space-y-1" {...props} />,
  ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-3 pl-4 space-y-1" {...props} />,
  li: ({node, ...props}) => <li className="mb-1" {...props} />,
  blockquote: ({node, ...props}) => <blockquote className="pl-4 italic border-l-4 border-slate-300 text-slate-600 dark:border-slate-600 dark:text-slate-400 my-3" {...props} />,
  code: ({
    node,
    inline,
    className, // from markdown: lang for fenced code blocks
    children,
    ...props // other HTML attributes
  }: {
    node?: any; 
    inline?: boolean;
    className?: string; 
    children: React.ReactNode;
  } & Omit<React.HTMLAttributes<HTMLElement>, 'className' | 'children'>) => {
    const match = /language-(\w+)/.exec(className || '');
    if (!inline && match) {
      // Block code
      // Background on pre, text color on code for specificity against prose.
      return (
        <pre className="block bg-slate-800 p-3 rounded-md my-3 overflow-x-auto text-sm dark:bg-slate-900">
          <code className={`language-${match[1]} text-slate-100 dark:text-slate-200`} {...props}>{children}</code>
        </pre>
      );
    }
    // Inline code
    return (
      <code className="px-1 py-0.5 bg-slate-200 text-slate-700 rounded text-sm dark:bg-slate-700 dark:text-slate-200" {...props}>{children}</code>
    );
  },
  img: ({node, ...props}) => <img className="max-w-full h-auto my-3 rounded-md border border-slate-300 dark:border-slate-600" {...props} />,
  table: ({node, ...props}) => <table className="table-auto w-full my-3 border-collapse border border-slate-300 dark:border-slate-600" {...props} />,
  th: ({node, ...props}) => <th className="border border-slate-300 dark:border-slate-600 px-3 py-1.5 bg-slate-100 dark:bg-slate-700 text-left font-semibold" {...props} />,
  td: ({node, ...props}) => <td className="border border-slate-300 dark:border-slate-600 px-3 py-1.5" {...props} />,
};

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ markdown }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[rehypeKatex]}
      components={markdownComponents} 
    >
      {markdown}
    </ReactMarkdown>
  );
};

export default MarkdownRenderer;