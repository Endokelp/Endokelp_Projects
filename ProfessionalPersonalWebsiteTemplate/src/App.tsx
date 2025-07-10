import React, { useEffect, useState } from 'react';
import { Analytics } from '@vercel/analytics/react';
import Header from './components/Header';
import Hero from './components/Hero';
import About from './components/About';
import Experience from './components/Experience';
import Skills from './components/Skills';
import Contact from './components/Contact';
import Footer from './components/Footer';
import AnimatedBackground from './components/AnimatedBackground';
import LoadingScreen from './components/LoadingScreen';
import MouseTrail from './components/MouseTrail';
import './styles/animations.css';
import './styles/cursor.css';
import './styles/liquid-glass.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Set page title
    document.title = "[Your Name] - Portfolio";
  }, []);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const handleLoadingComplete = () => {
    setIsLoading(false);
    // Reset scroll position when loading completes
    window.scrollTo(0, 0);
  };

  return (
    <>
      {isLoading && <LoadingScreen onComplete={handleLoadingComplete} />}
      
      <div className="min-h-screen transition-colors duration-300 bg-gray-900 text-white">
        <MouseTrail />
        <AnimatedBackground darkMode={true} />
        <div className="relative z-10">
          <Header />
          <main>
            <Hero />
            <About />
            <Experience />
            <Skills />
            <Contact />
          </main>
          <Footer />
        </div>
        <Analytics />
      </div>
    </>
  );
}

export default App;