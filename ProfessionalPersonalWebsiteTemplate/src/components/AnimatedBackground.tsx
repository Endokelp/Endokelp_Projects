import React, { useEffect, useState } from 'react';

interface AnimatedBackgroundProps {
  darkMode: boolean;
}

interface Star {
  id: number;
  x: number;
  y: number;
  size: number;
  opacity: number;
  glowIntensity: number;
  animationDelay: number;
}

interface RainDrop {
  id: number;
  x: number;
  y: number;
  speed: number;
  length: number;
  opacity: number;
}

const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({ darkMode }) => {
  const [stars, setStars] = useState<Star[]>([]);
  const [rainDrops, setRainDrops] = useState<RainDrop[]>([]);

  // Initialize stars for dark mode
  useEffect(() => {
    if (darkMode) {
      const newStars: Star[] = [];
      for (let i = 0; i < 60; i++) {
        newStars.push({
          id: i,
          x: Math.random() * 100,
          y: Math.random() * 100,
          size: Math.random() * 3 + 1,
          opacity: Math.random() * 0.8 + 0.2,
          glowIntensity: Math.random() * 0.5 + 0.5,
          animationDelay: Math.random() * 4
        });
      }
      setStars(newStars);
    }
  }, [darkMode]);

  // Initialize rain drops for light mode
  useEffect(() => {
    if (!darkMode) {
      const newRainDrops: RainDrop[] = [];
      for (let i = 0; i < 100; i++) {
        newRainDrops.push({
          id: i,
          x: Math.random() * 100,
          y: Math.random() * 100,
          speed: Math.random() * 2 + 1,
          length: Math.random() * 20 + 10,
          opacity: Math.random() * 0.4 + 0.1
        });
      }
      setRainDrops(newRainDrops);
    }
  }, [darkMode]);

  // Animate rain drops with better performance
  useEffect(() => {
    if (!darkMode) {
      const interval = setInterval(() => {
        setRainDrops(prevDrops => 
          prevDrops.map(drop => ({
            ...drop,
            y: drop.y >= 105 ? -10 : drop.y + drop.speed * 0.3
          }))
        );
      }, 60);

      return () => clearInterval(interval);
    }
  }, [darkMode]);

  if (darkMode) {
    return (
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        {stars.map(star => (
          <div
            key={star.id}
            className="absolute rounded-full animate-pulse"
            style={{
              left: `${star.x}%`,
              top: `${star.y}%`,
              width: `${star.size}px`,
              height: `${star.size}px`,
              backgroundColor: '#ffffff',
              opacity: star.opacity,
              boxShadow: `0 0 ${star.size * 4}px rgba(255, 255, 255, ${star.glowIntensity}), 0 0 ${star.size * 8}px rgba(147, 197, 253, ${star.glowIntensity * 0.5})`,
              animationDelay: `${star.animationDelay}s`,
              animationDuration: '3s'
            }}
          />
        ))}
        
        {/* Additional twinkling effect */}
        <div className="absolute inset-0 opacity-40">
          {Array.from({ length: 30 }).map((_, i) => (
            <div
              key={`twinkle-${i}`}
              className="absolute w-1 h-1 bg-blue-200 rounded-full animate-ping"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 6}s`,
                animationDuration: `${Math.random() * 4 + 2}s`
              }}
            />
          ))}
        </div>
        
        {/* Constellation lines effect */}
        <svg className="absolute inset-0 w-full h-full opacity-20" style={{ zIndex: -1 }}>
          {Array.from({ length: 8 }).map((_, i) => {
            const x1 = Math.random() * 100;
            const y1 = Math.random() * 100;
            const x2 = Math.random() * 100;
            const y2 = Math.random() * 100;
            return (
              <line
                key={`constellation-${i}`}
                x1={`${x1}%`}
                y1={`${y1}%`}
                x2={`${x2}%`}
                y2={`${y2}%`}
                stroke="rgba(147, 197, 253, 0.3)"
                strokeWidth="0.5"
                className="animate-pulse"
                style={{
                  animationDelay: `${Math.random() * 3}s`,
                  animationDuration: '4s'
                }}
              />
            );
          })}
        </svg>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {/* Rain drops */}
      {rainDrops.map(drop => (
        <div
          key={drop.id}
          className="absolute rounded-full"
          style={{
            left: `${drop.x}%`,
            top: `${drop.y}%`,
            width: '1.5px',
            height: `${drop.length}px`,
            opacity: drop.opacity,
            transform: 'rotate(15deg)',
            background: 'linear-gradient(to bottom, rgba(200, 220, 240, 0.7), rgba(160, 180, 200, 0.4))'
          }}
        />
      ))}
      
      {/* Natural rainy day atmosphere overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-400/10 via-gray-500/5 to-gray-600/15 backdrop-blur-[0.5px]" />
      
      {/* Subtle water droplets on glass effect */}
      {Array.from({ length: 25 }).map((_, i) => (
        <div
          key={`droplet-${i}`}
          className="absolute rounded-full backdrop-blur-sm"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: `${Math.random() * 12 + 3}px`,
            height: `${Math.random() * 12 + 3}px`,
            background: 'rgba(220, 230, 240, 0.15)',
            boxShadow: 'inset 0 1px 3px rgba(255, 255, 255, 0.3), 0 1px 4px rgba(0, 0, 0, 0.1)',
            animation: `float ${Math.random() * 6 + 4}s ease-in-out infinite`,
            animationDelay: `${Math.random() * 3}s`
          }}
        />
      ))}
      
      {/* Floating mist particles */}
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={`mist-particle-${i}`}
          className="absolute rounded-full backdrop-blur-md"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: `${Math.random() * 6 + 2}px`,
            height: `${Math.random() * 6 + 2}px`,
            background: 'rgba(240, 245, 250, 0.08)',
            animation: `drift ${Math.random() * 8 + 6}s linear infinite`,
            animationDelay: `${Math.random() * 4}s`
          }}
        />
      ))}
    </div>
  );
};

export default AnimatedBackground;