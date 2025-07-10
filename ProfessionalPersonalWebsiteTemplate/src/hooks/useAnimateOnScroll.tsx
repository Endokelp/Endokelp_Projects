import { useEffect, useRef } from 'react';

interface AnimateOnScrollOptions {
  threshold?: number;
  rootMargin?: string;
}

export function useAnimateOnScroll<T extends HTMLElement>(
  options: AnimateOnScrollOptions = {}
) {
  const ref = useRef<T>(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      },
      { 
        threshold: options.threshold || 0.1,
        rootMargin: options.rootMargin || '0px' 
      }
    );

    if (ref.current) observer.observe(ref.current);

    return () => {
      if (ref.current) observer.unobserve(ref.current);
    };
  }, [options.threshold, options.rootMargin]);

  return ref;
}