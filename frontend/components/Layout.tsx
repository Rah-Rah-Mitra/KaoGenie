import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-sky-100 dark:from-slate-800 dark:to-sky-900 flex flex-col">
      <main className="flex-grow">
        {children}
      </main>
      <footer className="bg-slate-800 text-slate-300 dark:bg-slate-900 dark:text-slate-400 p-4 text-center text-sm">
        © {new Date().getFullYear()} AI Exam Generator. All rights reserved.
      </footer>
    </div>
  );
};

export default Layout;