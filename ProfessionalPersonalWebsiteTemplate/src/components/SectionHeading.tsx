import React, { ReactNode } from 'react';

interface SectionHeadingProps {
  children: ReactNode;
}

const SectionHeading: React.FC<SectionHeadingProps> = ({ children }) => {
  return (
    <div className="flex items-center mb-8">
      <h2 className="text-2xl md:text-3xl font-bold text-white">
        {children}
      </h2>
      <div className="h-px bg-white/50 dark:bg-gray-700 flex-grow ml-6"></div>
    </div>
  );
};

export default SectionHeading;