import React from 'react';

export const LumonLogo = ({ className = "w-8 h-8" }: { className?: string }) => {
  return (
    <svg viewBox="0 0 100 100" className={className} fill="none" stroke="currentColor" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="50" cy="50" rx="45" ry="30" />
      <line x1="15" y1="35" x2="85" y2="35" />
      <line x1="15" y1="65" x2="85" y2="65" />
      <path d="M 35 23 C 20 40 20 60 35 77" />
      <path d="M 65 23 C 80 40 80 60 65 77" />
    </svg>
  );
};

export const LumonText = ({ className = "", textClass = "text-natural-charcoal", dotClass = "fill-natural-charcoal" }: { className?: string, textClass?: string, dotClass?: string }) => {
  return (
    <span className={`font-display font-bold tracking-[0.2em] uppercase flex items-center ${textClass} ${className}`}>
      LUM
      <span className="relative flex items-center justify-center mx-[1px]">
        O
        <span className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <svg viewBox="0 0 10 10" className={`w-[0.35em] h-[0.35em] ${dotClass}`} style={{ transform: 'translateY(5%)' }}>
            <path d="M5 0C5 0 1.5 4.5 1.5 6.5C1.5 8.433 3.067 10 5 10C6.933 10 8.5 8.433 8.5 6.5C8.5 4.5 5 0 5 0Z"/>
          </svg>
        </span>
      </span>
      N
    </span>
  );
};
