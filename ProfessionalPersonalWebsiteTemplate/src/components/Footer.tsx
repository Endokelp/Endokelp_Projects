import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="py-8 border-t border-white/30 dark:border-gray-800">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-gray-400 mb-4 md:mb-0">
            Designed & Built by [Your Name]
          </p>
          
          <p className="text-sm text-gray-400 mt-2">
            © {new Date().getFullYear()} All Rights Reserved
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;