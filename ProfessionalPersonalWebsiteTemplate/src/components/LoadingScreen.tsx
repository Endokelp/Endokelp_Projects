import React, { useState, useEffect } from 'react';

interface LoadingScreenProps {
  onComplete: () => void;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ onComplete }) => {
  const [scale, setScale] = useState(1);
  const [opacity, setOpacity] = useState(1);
  const [showHint, setShowHint] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Check if device is mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768 || 'ontouchstart' in window);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    // Show hint after 2 seconds
    const hintTimer = setTimeout(() => {
      setShowHint(true);
    }, 2000);

    return () => {
      window.removeEventListener('resize', checkMobile);
      clearTimeout(hintTimer);
    };
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      if (!isMobile) {
        const scrollY = window.scrollY;
        const maxScroll = 600; // Increased from 300 to make animation twice as slow
        const newScale = 1 + (scrollY / maxScroll) * 2; // Scale from 1 to 3
        const newOpacity = Math.max(0, 1 - (scrollY / maxScroll));
        
        setScale(newScale);
        setOpacity(newOpacity);
        
        if (scrollY >= maxScroll) {
          setTimeout(() => onComplete(), 300);
        }
      }
    };

    const handleClick = () => {
      if (isMobile) {
        setScale(3);
        setOpacity(0);
        setTimeout(() => onComplete(), 500);
      }
    };

    if (!isMobile) {
      window.addEventListener('scroll', handleScroll);
    }
    
    const loadingElement = document.getElementById('loading-screen');
    if (loadingElement && isMobile) {
      loadingElement.addEventListener('click', handleClick);
    }

    return () => {
      if (!isMobile) {
        window.removeEventListener('scroll', handleScroll);
      }
      if (loadingElement && isMobile) {
        loadingElement.removeEventListener('click', handleClick);
      }
    };
  }, [isMobile, onComplete]);

  return (
    <div
      id="loading-screen"
      className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 overflow-hidden"
      style={{ opacity }}
    >
      <div className="relative">
        <img
          src="/loading.png"
          alt="Loading"
          className="transition-transform duration-300 ease-out"
          style={{
            transform: `scale(${scale})`,
            maxWidth: '80vw',
            maxHeight: '80vh',
            objectFit: 'contain'
          }}
        />
        
        {showHint && (
          <div className="absolute bottom-[-80px] left-1/2 transform -translate-x-1/2 text-center">
            <p className="text-white text-lg mb-4 animate-pulse">
              {isMobile ? 'Tap the painting to enter' : 'Scroll down to zoom in'}
            </p>
            {!isMobile && (
              <div className="flex justify-center">
                <div className="animate-bounce">
                  <svg
                    className="w-6 h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default LoadingScreen;