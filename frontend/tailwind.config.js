/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'rounded': ['"M PLUS Rounded 1c"', 'sans-serif'],
      },
      animation: {
        'shake': 'shake 0.2s ease-in-out',
        'fly-up': 'fly-up 0.8s ease-out forwards',
        'fade-in-up': 'fadeInUp 0.4s ease-out forwards',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        shake: {
          '0%, 100%': { transform: 'translate(0, 0) scale(0.95)' },
          '25%': { transform: 'translate(-5px, 5px) scale(0.95)' },
          '50%': { transform: 'translate(5px, -5px) scale(0.95)' },
          '75%': { transform: 'translate(-5px, -5px) scale(0.95)' },
        },
        'fly-up': {
          '0%': { opacity: '1', transform: 'translateY(0) scale(1)' },
          '100%': { opacity: '0', transform: 'translateY(-50px) scale(1.5)' },
        },
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
