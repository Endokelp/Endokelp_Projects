import React from 'react';
import SectionHeading from './SectionHeading';
import { useAnimateOnScroll } from '../hooks/useAnimateOnScroll';

const About: React.FC = () => {
  const sectionRef = useAnimateOnScroll<HTMLDivElement>();
  const textRef = useAnimateOnScroll<HTMLDivElement>({ threshold: 0.2 });
  const imageRef = useAnimateOnScroll<HTMLDivElement>({ threshold: 0.2, rootMargin: '50px' });
  
  return (
    <section id="about" className="py-20">
      <div className="container mx-auto px-4 md:px-6" ref={sectionRef}>
        <SectionHeading>About Me</SectionHeading>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 items-start mt-12">
          <div className="md:col-span-2 opacity-0" ref={textRef}>
            <p className="text-white/90 dark:text-gray-300 mb-4 leading-relaxed drop-shadow-lg">
              I'm a passionate developer and aspiring innovator based in [Your City, State].
            </p>
            
            <p className="text-gray-300 mb-4 leading-relaxed">
              I love solving meaningful problems with code. My interests span [Your Interests]. Over the last year, I've built various projects that showcase my skills.
            </p>
            
            <p className="text-gray-300 mb-4 leading-relaxed">
              My goal is to build transformative products and grow as a developer. I'm constantly learning and building to make that vision a reality.
            </p>
            
            <p className="text-gray-300 mb-6 leading-relaxed">
              When I'm not coding, you can find me [Your Hobbies/Activities].
            </p>
            
            <div className="bg-white/5 dark:bg-gray-800/50 rounded-lg p-6 border border-white/10 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                <span className="text-indigo-400 mr-2">💡</span>
                What is [Your Persona/Project Name]?
              </h3>
              <p className="text-gray-300 leading-relaxed">
                [Your Persona/Project Name] is my online persona. [Add a brief, generalized description here].
              </p>
            </div>
          </div>
          
          <div className="relative group opacity-0" ref={imageRef}>
            <div className="relative rounded-lg overflow-hidden border-2 border-indigo-600/20 dark:border-indigo-400/20">
              <div className="w-full h-80 bg-gray-200 dark:bg-gray-700 rounded-lg shadow-lg flex items-center justify-center">
                <span className="text-gray-500 dark:text-gray-400 text-lg font-medium">Insert Picture Here</span>
              </div>
              <div className="absolute inset-0 bg-indigo-600/10 dark:bg-indigo-400/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </div>
            
            <div className="absolute -z-10 -inset-0.5 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-500 dark:to-purple-500 opacity-30 blur group-hover:opacity-100 transition duration-300 group-hover:duration-200"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;