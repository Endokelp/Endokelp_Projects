import React from 'react';

interface Experience {
  id: string;
  title: string;
  company: string;
  date: string;
  description: string[];
}

interface ExperienceCardProps {
  experience: Experience;
}

const ExperienceCard: React.FC<ExperienceCardProps> = ({ experience }) => {
  return (
    <div className="p-6 bg-black/30 dark:bg-gray-800 rounded-lg shadow-sm transition-all duration-300 h-full backdrop-blur-sm border border-white/20 dark:border-gray-700">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-white dark:text-white drop-shadow-lg">
          {experience.title} <span className="text-indigo-600 dark:text-indigo-400">@ {experience.company}</span>
        </h3>
        <p className="text-sm text-white/80 dark:text-gray-400 mt-1 drop-shadow-lg">{experience.date}</p>
      </div>
      
      <ul className="space-y-3">
        {experience.description.map((item, index) => (
          <li key={index} className="flex items-start">
            <span className="text-indigo-600 dark:text-indigo-400 mr-2 mt-1.5">▹</span>
            <span className="text-white/90 dark:text-gray-300 drop-shadow-lg">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ExperienceCard;