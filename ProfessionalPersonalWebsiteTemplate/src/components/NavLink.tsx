import React, { useEffect, useState } from 'react';

interface NavLinkProps {
  href: string;
  label: string;
  onClick?: () => void;
}

const NavLink: React.FC<NavLinkProps> = ({ href, label, onClick }) => {
  const [isActive, setIsActive] = useState(false);
  
  useEffect(() => {
    const handleScroll = () => {
      const section = document.querySelector(href);
      if (section) {
        const rect = section.getBoundingClientRect();
        const isInView = rect.top <= 100 && rect.bottom >= 100;
        setIsActive(isInView);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    // Initial check
    handleScroll();
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, [href]);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    
    // Get current and target sections
    const currentSection = document.querySelector('[id]');
    const targetSection = document.querySelector(href);
    
    if (targetSection && currentSection) {
      // Check if we're scrolling up
      const currentRect = currentSection.getBoundingClientRect();
      const targetRect = targetSection.getBoundingClientRect();
      const isScrollingUp = targetRect.top < currentRect.top;
      
      if (isScrollingUp) {
        // Apply scroll-up animation to current section if scrolling up
        document.querySelectorAll('section').forEach(section => {
          if (section.getBoundingClientRect().top > targetRect.top && 
              section.getBoundingClientRect().top < window.innerHeight) {
            section.classList.add('scroll-up');
            setTimeout(() => section.classList.remove('scroll-up'), 800);
          }
        });
      }
      
      // Smooth scroll to target section
      targetSection.scrollIntoView({
        behavior: 'smooth'
      });
    }
    
    if (onClick) onClick();
  };

  return (
    <li>
      <a
        href={href}
        onClick={handleClick}
        className={`relative text-base font-medium hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors py-1 
          ${isActive 
            ? 'text-indigo-600 dark:text-indigo-400' 
            : 'text-gray-700 dark:text-gray-300'
          }`}
      >
        {label}
        <span 
          className={`absolute -bottom-1 left-0 w-full h-0.5 bg-indigo-600 dark:bg-indigo-400 transform origin-left transition-transform duration-300 
            ${isActive ? 'scale-x-100' : 'scale-x-0'}`}
        />
      </a>
    </li>
  );
};

export default NavLink;