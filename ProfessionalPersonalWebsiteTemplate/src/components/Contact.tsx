import React from 'react';
import SectionHeading from './SectionHeading';

const Contact: React.FC = () => {
  return (
    <section id="contact" className="py-20 bg-transparent">
      <div className="container mx-auto px-4 md:px-6">
        <SectionHeading>Get in Touch</SectionHeading>
        
        <div className="max-w-2xl mx-auto mt-12 text-center">
          <p className="text-lg text-gray-300 mb-8 leading-relaxed">
            Email works best. I’m not great at checking DMs everywhere.
          </p>
          
          <div className="mb-10">
            <a 
              href="mailto:venni.devireddy@gmail.com" 
              className="inline-flex items-center justify-center px-8 py-4 text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md shadow-sm transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
            >
              Email me
            </a>
          </div>
          
          <div className="flex justify-center space-x-6">
            <a 
              href="mailto:venni.devireddy@gmail.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-300 hover:text-indigo-400 transition-colors duration-300"
              aria-label="Email"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
              </svg>
            </a>
            <a 
              href="https://github.com/Endokelp" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-300 hover:text-indigo-400 transition-colors duration-300"
              aria-label="GitHub"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
              </svg>
            </a>
          </div>
          
          <p className="text-sm text-gray-500 mt-6">
            No blog linked yet—if I start one I’ll wire it here.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Contact;