import React, { useRef, useEffect } from 'react';
import TicTacToe from './TicTacToe';

const Hero: React.FC = () => {
  const nameRef = useRef<HTMLHeadingElement>(null);
  const descriptionRef = useRef<HTMLHeadingElement>(null);
  const introRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      },
      { threshold: 0.1 }
    );

    if (nameRef.current) observer.observe(nameRef.current);
    if (descriptionRef.current) observer.observe(descriptionRef.current);
    if (introRef.current) observer.observe(introRef.current);

    return () => {
      if (nameRef.current) observer.unobserve(nameRef.current);
      if (descriptionRef.current) observer.unobserve(descriptionRef.current);
      if (introRef.current) observer.unobserve(introRef.current);
    };
  }, []);

  return (
    <section id="hero" className="min-h-screen flex items-center pt-16 pb-16">
      <div className="container mx-auto px-4 md:px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="max-w-3xl">
            <p className="text-indigo-400 font-medium mb-5 opacity-0 transform translate-y-4 transition-all duration-700 delay-300 ease-out" ref={introRef}>
              Hi, my name is
            </p>
            <h1 
              className="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-4 opacity-0 transform translate-y-4 transition-all duration-700 delay-300 ease-out"
              ref={nameRef}
            >
              [Your Name]
            </h1>
            <h2 
              className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-300 mb-6 opacity-0 transform translate-y-4 transition-all duration-700 delay-700 ease-out"
              ref={descriptionRef}
            >
              I build things for the web.
            </h2>
            <p className="text-lg text-gray-400 mb-8 max-w-2xl leading-relaxed">
              I'm a software developer specializing in building (and occasionally designing) exceptional digital experiences. Currently, I'm focused on building accessible, human-centered products at [Your Company/Project].
            </p>
            <div className="flex flex-wrap gap-4">
              <a 
                href="#contact" 
                className="px-6 py-3 rounded-md bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                onClick={(e) => {
                  e.preventDefault();
                  document.querySelector('#contact')?.scrollIntoView({
                    behavior: 'smooth'
                  });
                }}
              >
                Get in touch
              </a>
              <a 
                href="#experience" 
                className="px-6 py-3 rounded-md bg-transparent text-white border border-gray-700 font-medium hover:bg-gray-800 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-900"
                onClick={(e) => {
                  e.preventDefault();
                  document.querySelector('#experience')?.scrollIntoView({
                    behavior: 'smooth'
                  });
                }}
              >
                See my work
              </a>
            </div>
          </div>
          
          <div className="flex justify-center lg:justify-end">
            <TicTacToe />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;