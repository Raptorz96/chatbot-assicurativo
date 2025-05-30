/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // 🎨 COLOR PALETTE - Insurance Professional Theme
      colors: {
        // Primary - Professional Blue (fiducia, stabilità)
        primary: {
          50: '#eff6ff',
          100: '#dbeafe', 
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // Main brand
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554'
        },
        
        // Accent - Trust Green (successo, sicurezza)  
        accent: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e', // Success states
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d'
        },
        
        // Warning - Professional Orange (attenzione)
        warning: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa', 
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316', // Warning states
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12'
        },
        
        // Error - Professional Red (errori, emergenze)
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5', 
          400: '#f87171',
          500: '#ef4444', // Error states
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d'
        },
        
        // Neutral - Modern Grays (interfaccia, testi)
        neutral: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617'
        }
      },
      
      // 🌟 GLASSMORPHISM EFFECTS
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        DEFAULT: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '40px',
        '3xl': '64px',
      },
      
      // 📐 SPACING SCALE (basato su 4px grid)
      spacing: {
        '18': '4.5rem',   // 72px
        '88': '22rem',    // 352px
        '128': '32rem',   // 512px
        '144': '36rem',   // 576px
      },
      
      // 📝 TYPOGRAPHY SCALE
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'Monaco', 'monospace'],
      },
      
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],     // 12px
        'sm': ['0.875rem', { lineHeight: '1.25rem' }], // 14px  
        'base': ['1rem', { lineHeight: '1.5rem' }],    // 16px
        'lg': ['1.125rem', { lineHeight: '1.75rem' }], // 18px
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],  // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }],     // 24px
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],   // 36px
        '5xl': ['3rem', { lineHeight: '1' }],           // 48px
      },
      
      // 🎭 ANIMATION DURATIONS  
      transitionDuration: {
        '250': '250ms',
        '400': '400ms', 
        '600': '600ms',
      },
      
      // 📊 BORDER RADIUS (rounded corners moderni)
      borderRadius: {
        'none': '0',
        'sm': '0.125rem',   // 2px
        'DEFAULT': '0.25rem', // 4px
        'md': '0.375rem',   // 6px
        'lg': '0.5rem',     // 8px
        'xl': '0.75rem',    // 12px
        '2xl': '1rem',      // 16px
        '3xl': '1.5rem',    // 24px
        'full': '9999px',
      },
      
      // 🌊 SHADOWS (depth e glassmorphism)
      boxShadow: {
        // Glass effect shadows
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        'glass-lg': '0 25px 50px -12px rgba(31, 38, 135, 0.25)',
        
        // Professional shadows
        'soft': '0 2px 8px 0 rgba(0, 0, 0, 0.08)',
        'medium': '0 4px 16px 0 rgba(0, 0, 0, 0.12)',
        'strong': '0 8px 24px 0 rgba(0, 0, 0, 0.16)',
        
        // Colored shadows per brand
        'primary': '0 4px 14px 0 rgba(59, 130, 246, 0.3)',
        'accent': '0 4px 14px 0 rgba(34, 197, 94, 0.3)',
        'warning': '0 4px 14px 0 rgba(249, 115, 22, 0.3)',
        'error': '0 4px 14px 0 rgba(239, 68, 68, 0.3)',
      },
      
      // 📐 GRID SYSTEM
      gridTemplateColumns: {
        'sidebar': '240px 1fr',
        'dashboard': 'repeat(auto-fit, minmax(280px, 1fr))',
      },
      
      // 🎯 Z-INDEX SCALE (layering system)
      zIndex: {
        'dropdown': '1000',
        'modal': '1050', 
        'popover': '1060',
        'tooltip': '1070',
        'navbar': '1080',
      },
      
      // ⚡ ANIMATIONS PERSONALIZZATE
      keyframes: {
        // Fade in con movimento
        'fade-in-up': {
          '0%': {
            opacity: '0',
            transform: 'translateY(10px)',
          },
          '100%': {
            opacity: '1', 
            transform: 'translateY(0)',
          },
        },
        
        // Pulse soft per loading
        'pulse-soft': {
          '0%, 100%': {
            opacity: '1',
          },
          '50%': {
            opacity: '0.5',
          },
        },
        
        // Slide in da sinistra
        'slide-in-left': {
          '0%': {
            opacity: '0',
            transform: 'translateX(-100%)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateX(0)',
          },
        },
        
        // Shimmer per skeleton loading
        'shimmer': {
          '0%': {
            backgroundPosition: '-468px 0',
          },
          '100%': {
            backgroundPosition: '468px 0', 
          },
        },
      },
      
      animation: {
        'fade-in-up': 'fade-in-up 0.5s ease-out',
        'pulse-soft': 'pulse-soft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in-left': 'slide-in-left 0.3s ease-out',
        'shimmer': 'shimmer 1.2s ease-in-out infinite',
      },
    },
  },
  
  // 🔌 PLUGINS per funzionalità avanzate
  plugins: [
    // Note: Install these if needed
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
    // require('@tailwindcss/aspect-ratio'),
  ],
}