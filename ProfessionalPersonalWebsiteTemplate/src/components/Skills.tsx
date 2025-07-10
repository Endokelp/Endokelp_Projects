import React from 'react';
import SectionHeading from './SectionHeading';
import { useAnimateOnScroll } from '../hooks/useAnimateOnScroll';

interface SkillCategory {
  name: string;
  skills: string[];
}

const skillCategories: SkillCategory[] = [
  {
    name: 'Languages',
    skills: ['JavaScript (ES6+)', 'TypeScript', 'Python', 'HTML/CSS']
  },
  {
    name: 'Frameworks',
    skills: ['React', 'Vue', 'Node.js', 'Express']
  },
  {
    name: 'Tools',
    skills: ['Webpack', 'Babel', 'Git & GitHub', 'Docker', 'Figma']
  },
  {
    name: 'Other',
    skills: ['Agile Methodologies', 'CI/CD', 'Testing (Jest, Cypress)']
  }
];

const Skills: React.FC = () => {
  const sectionRef = useAnimateOnScroll<HTMLDivElement>();
  
  return (
    <section id="skills" className="py-20">
      <div className="container mx-auto px-4 md:px-6" ref={sectionRef}>
        <SectionHeading>Skills</SectionHeading>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mt-12">
          {skillCategories.map((category, index) => {
            // Create a staggered animation effect
            const categoryRef = useAnimateOnScroll<HTMLDivElement>({ 
              threshold: 0.1,
              rootMargin: `${index * 50}px` 
            });
            
            return (
              <div 
                key={category.name}
                ref={categoryRef}
                className="liquid-glass-card dark:liquid-glass-card-dark rain-behind-glass p-6 opacity-0 relative z-10"
              >
                <h3 className="text-lg font-semibold text-white mb-4 border-b border-gray-700 pb-2">
                  {category.name}
                </h3>
                
                <ul className="space-y-2">
                  {category.skills.map((skill) => (
                    <li 
                      key={skill} 
                      className="flex items-center text-gray-300"
                    >
                      <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2"></span>
                      {skill}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Skills;