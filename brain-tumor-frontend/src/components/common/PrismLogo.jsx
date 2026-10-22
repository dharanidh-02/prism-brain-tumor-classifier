import React from 'react';

/**
 * Original geometric PRISM symbol.
 * Combines an optical refraction prism with a neural node graph and cranial cross-sections.
 */
export default function PrismLogo({ size = 32, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="PRISM Logo"
    >
      <defs>
        <linearGradient id="prism-grad-main" x1="6" y1="42" x2="42" y2="6" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#4f46e5" />
          <stop offset="50%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#0d9488" />
        </linearGradient>
        <linearGradient id="prism-grad-internal" x1="16" y1="36" x2="32" y2="12" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#818cf8" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#2dd4bf" stopOpacity="0.8" />
        </linearGradient>
      </defs>

      {/* Outer Prism Tetrahedron Triangle */}
      <path
        d="M24 6L42 39H6L24 6Z"
        stroke="url(#prism-grad-main)"
        strokeWidth="3.2"
        strokeLinejoin="round"
      />

      {/* Neural Core Inverted Reflection */}
      <path
        d="M24 16L33 34H15L24 16Z"
        stroke="url(#prism-grad-internal)"
        strokeWidth="2.2"
        strokeLinejoin="round"
      />

      {/* Optical Focal Beam Lines */}
      <line x1="24" y1="6" x2="24" y2="16" stroke="#4f46e5" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="6" y1="39" x2="15" y2="34" stroke="#6366f1" strokeWidth="2.2" strokeLinecap="round" />
      <line x1="42" y1="39" x2="33" y2="34" stroke="#0d9488" strokeWidth="2.2" strokeLinecap="round" />

      {/* Central Neural Attention Node */}
      <circle cx="24" cy="27" r="3.2" fill="#4f46e5" />
      <circle cx="24" cy="27" r="5" stroke="#818cf8" strokeWidth="1" strokeDasharray="2 2" />
    </svg>
  );
}
