import React, { useEffect, useState } from 'react';

const MouseTrail: React.FC = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    document.addEventListener('mousemove', handleMouseMove);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-40">
      {/* Cursor aura - larger outer glow */}
      <div
        className="absolute rounded-full pointer-events-none"
        style={{
          left: mousePosition.x - 30,
          top: mousePosition.y - 30,
          width: '60px',
          height: '60px',
          background: 'radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.1) 40%, transparent 70%)',
          boxShadow: '0 0 40px rgba(99, 102, 241, 0.4), 0 0 80px rgba(99, 102, 241, 0.2)',
          transition: 'all 0.15s ease-out'
        }}
      />
      
      {/* Inner cursor glow */}
      <div
        className="absolute rounded-full pointer-events-none"
        style={{
          left: mousePosition.x - 15,
          top: mousePosition.y - 15,
          width: '30px',
          height: '30px',
          background: 'radial-gradient(circle, rgba(99, 102, 241, 0.6) 0%, rgba(99, 102, 241, 0.3) 50%, transparent 100%)',
          boxShadow: '0 0 20px rgba(99, 102, 241, 0.6)',
          transition: 'all 0.1s ease-out'
        }}
      />
    </div>
  );
};

export default MouseTrail;