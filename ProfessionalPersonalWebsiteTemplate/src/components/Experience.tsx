import React, { useState } from 'react';
import SectionHeading from './SectionHeading';
import ExperienceCard from './ExperienceCard';
import { useAnimateOnScroll } from '../hooks/useAnimateOnScroll';

interface Experience {
  id: string;
  title: string;
  company: string;
  date: string;
  description: string[];
}

const experiences: Experience[] = [
  {
    id: 'public',
    title: 'Projects & coursework',
    company: 'GitHub',
    date: 'ongoing',
    description: [
      'Public code is under github.com/Endokelp (games, templates, Java homework, Python experiments).',
      'I’m not inventing fake company names here—if I add a real job later, it’ll show up in this section.',
    ],
  },
];

const Experience: React.FC = () => {
  const [selectedExperience, setSelectedExperience] = useState<string>(experiences[0].id);
  const sectionRef = useAnimateOnScroll<HTMLDivElement>();
  const tabsRef = useAnimateOnScroll<HTMLDivElement>({ threshold: 0.2 });
  const contentRef = useAnimateOnScroll<HTMLDivElement>({ threshold: 0.2 });

  const selectedExp = experiences.find(exp => exp.id === selectedExperience) || experiences[0];

  return (
    <section id="experience" className="py-20 bg-transparent">
      <div className="container mx-auto px-4 md:px-6" ref={sectionRef}>
        <SectionHeading>Experience</SectionHeading>
        
        <div className="mt-12 grid grid-cols-1 md:grid-cols-12 gap-8">
          <div className="md:col-span-4 lg:col-span-3 opacity-0" ref={tabsRef}>
            <div className="flex flex-row md:flex-col overflow-x-auto md:overflow-x-visible space-x-4 md:space-x-0 md:space-y-1 p-1">
              {experiences.map((exp) => (
                <button
                  key={exp.id}
                  onClick={() => setSelectedExperience(exp.id)}
                  className={`px-4 py-3 text-left rounded-md transition-colors whitespace-nowrap md:whitespace-normal
                    ${selectedExperience === exp.id
                      ? 'bg-white/20 text-indigo-400 dark:bg-gray-800 dark:text-indigo-400 font-medium backdrop-blur-sm border border-white/30 dark:border-gray-700'
                      : 'text-white/80 dark:text-gray-400 hover:bg-white/10 dark:hover:bg-gray-800/50 drop-shadow-lg'
                    }`}
                >
                  {exp.company}
                </button>
              ))}
            </div>
          </div>
          
          <div className="md:col-span-8 lg:col-span-9 opacity-0" ref={contentRef}>
            <ExperienceCard experience={selectedExp} />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Experience;