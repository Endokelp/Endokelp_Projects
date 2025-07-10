import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import NavLink from './NavLink';

interface HeaderProps {}

const Header: React.FC<HeaderProps> = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    if (!isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
    document.body.style.overflow = 'auto';
  };

  const scrollToTop = (e: React.MouseEvent) => {
    e.preventDefault();
    
    // Apply scroll-up animation to visible sections
    document.querySelectorAll('section').forEach(section => {
      if (section.getBoundingClientRect().top < window.innerHeight && 
          section.getBoundingClientRect().bottom > 0) {
        section.classList.add('scroll-up');
        setTimeout(() => section.classList.remove('scroll-up'), 800);
      }
    });
    
    // Scroll to top
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
    
    closeMenu();
  };

  return (
    <header 
      className={`fixed w-full z-50 transition-all duration-300 ${
        scrolled 
          ? 'py-4 bg-white/10 backdrop-blur-md dark:bg-gray-900/80' 
          : 'py-6 bg-transparent'
      }`}
    >
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex items-center justify-between">
          <a 
            href="#hero" 
            className="text-xl font-semibold tracking-tight text-gray-900 dark:text-white"
            onClick={scrollToTop}
          >
            <span className="text-indigo-600 dark:text-indigo-400">[Your Name]</span>
          </a>
          
          <div className="flex items-center space-x-4">
            <nav className="hidden md:block">
              <ul className="flex space-x-8">
                <NavLink href="#about" label="About" onClick={closeMenu} />
                <NavLink href="#experience" label="Experience" onClick={closeMenu} />
                <NavLink href="#skills" label="Skills" onClick={closeMenu} />
                <NavLink href="#contact" label="Contact" onClick={closeMenu} />
              </ul>
            </nav>
            

            
            <button
              className="md:hidden p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
              onClick={toggleMenu}
              aria-label="Toggle menu"
            >
              {isMenuOpen ? (
                <X size={24} className="text-gray-800 dark:text-gray-200" />
              ) : (
                <Menu size={24} className="text-gray-800 dark:text-gray-200" />
              )}
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div 
        className={`fixed inset-0 bg-white dark:bg-gray-900 z-40 transform transition-transform duration-300 ease-in-out ${
          isMenuOpen ? 'translate-x-0' : 'translate-x-full'
        } md:hidden`}
      >
        <div className="flex flex-col h-full justify-center items-center space-y-8 pt-16">
          <NavLink href="#about" label="About" onClick={closeMenu} />
          <NavLink href="#experience" label="Experience" onClick={closeMenu} />
          <NavLink href="#skills" label="Skills" onClick={closeMenu} />
          <NavLink href="#contact" label="Contact" onClick={closeMenu} />
        </div>
      </div>
    </header>
  );
};

export default Header;