import { useState, type ReactNode } from 'react';

export function Tooltip({ children, text }: { children: ReactNode; text: string }) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative inline-block" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <div className="absolute z-10 bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 text-xs bg-surface-light text-text rounded-lg whitespace-nowrap shadow-lg">
          {text}
        </div>
      )}
    </div>
  );
}
