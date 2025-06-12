/** @type {import('tailwindcss').Config} */
const plugin = require('tailwindcss/plugin')
const flattenColorPalette = require('tailwindcss/lib/util/flattenColorPalette').default;

// tailwind.config.js
module.exports = {
  content: [
    "../templates/**/*.html", // Indica dove cercare le classi Tailwind
    "../**/templates/**/*.html",
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {
      scale: {
        '0': '0',
        '97': '0.97', 
        '98': '0.98', 
        '99': '0.99', 
        '101': '1.01', 
      },
      maxHeight: {
        768: "768px",
      },
      boxShadow: {
        // Ombre personalizzate con opacità differenziate
        'inner-horizontal': 'inset 15px 0 15px -15px rgba(0, 0, 0, 0.3), inset -15px 0 15px -15px rgba(0, 0, 0, 0.3)', // Ombra interna solo ai lati
        "uniform-sm": "0 0 5px 2px rgba(0, 0, 0, 0.1)", // Piccola ombra uniforme
        "uniform-md": "0 0 10px 4px rgba(0, 0, 0, 0.2)", // Media ombra uniforme
        "uniform-lg": "0 0 15px 6px rgba(0, 0, 0, 0.3)", // Grande ombra uniforme
        "uniform-xl": "0 0 20px 8px rgba(0, 0, 0, 0.35)", // Ombra extra-large uniforme
        "uniform-2xl": "0 0 30px 12px rgba(0, 0, 0, 0.4)", // Ombra 2xl uniforme
        "3xl": "0 25px 50px -12px rgb(0 0 0 / 0.5)", // Ombra 3xl
        "uniform-inner": "inset 0 0 10px 5px rgba(0, 0, 0, 0.2)", // Ombra interna uniforme
      },
      minHeight: {
        "vh-minus-12": "calc(100vh - 3rem)", // Altezza minima che sottrae 3rem dall'altezza della viewport
        "vh-minus-16": "calc(100vh - 4rem)", // Altezza minima che sottrae 4rem dall'altezza della viewport
        "vh-minus-24": "calc(100vh - 6rem)", // Altezza minima che sottrae 6rem dall'altezza della viewport
      },
      height: {
        "vh-minus-12": "calc(100vh - 3rem)", // Definisci una classe personalizzata che sottrae l'altezza della navbar
        "vh-minus-16": "calc(100vh - 4rem)", // Definisci una classe personalizzata che sottrae l'altezza della navbar
        "vh-minus-24": "calc(100vh - 6rem)", // Definisci una classe personalizzata che sottrae l'altezza della navbar
      },
      animation: {
        slideDown: 'slideDown 1s ease-out forwards',
        slideUp: 'slideUp 1s ease-out forwards',
        expandHeight: 'expandHeight 0.5s ease-out forwards',
        collapseHeight: 'collapseHeight 0.5s ease-out forwards',
        fadeIn: 'fadeIn 1.5s ease-out forwards',
        fadeOut: 'fadeOut 0.5s ease-out forwards',
        'bounce-up': 'bounce-up 0.6s ease-in-out 0s 2 forwards',
        'gradient': "animatedgradient 3s ease infinite alternate",
        'slide-in': 'slide-in 0.5s ease-out forwards',
        'bounce-in': 'bounce-in 0.5s ease-in-out forwards',
        'zoom-in': 'zoom-in 0.5s ease-out forwards',
        'flip-in': 'flip-in 0.7s ease-out forwards',
        'fade-in-delayed': 'fade-in 2.5s ease-out 1.5s forwards',
        fadeCollapse: 'fadeCollapse 0.5s ease-in-out forwards',
        'pulse-shadow': 'pulse-shadow-generic 2.5s infinite',
      },
      keyframes: {
        fadeCollapse: {
          '0%': { opacity: '1', height: '100%' },
          '25%': { opacity: '0', height: '100%' },
          '100%': { opacity: '0', height: '0' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        expandHeight: {
          '0%': { height: '0', opacity: '0' },
          '100%': { height: 'auto', opacity: '1' },
        },
        collapseHeight: {
          '0%': { height: 'auto', opacity: '1' },
          '100%': { height: '0', opacity: '0' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        'bounce-up': {
          '0%': { transform: 'translateY(0)' },
          '30%': { transform: 'translateY(-30px)' }, // Salta verso l'alto
          '50%': { transform: 'translateY(0)' },     // Ritorna alla posizione originale
          '70%': { transform: 'translateY(-16px)' }, // Rimbalzo minore
          '100%': { transform: 'translateY(0)' },    // Fermo in posizione originale
        },
        'animatedgradient': {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-in': {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'bounce-in': {
          '0%': { transform: 'scale(0.5)', opacity: '0' },
          '50%': { transform: 'scale(1.2)', opacity: '1' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'zoom-in': {
          '0%': { transform: 'scale(0.5)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'flip-in': {
          '0%': { transform: 'rotateY(180deg)', opacity: '0' },
          '100%': { transform: 'rotateY(0deg)', opacity: '1' },
        },
        'pulse-shadow-generic': {
          '0%': {
            boxShadow: '0 0 0 0 var(--tw-shadow-color)',
          },
          '50%': {
            boxShadow: '0 0 2.5px 5px transparent',
          },
          '100%': {
            boxShadow: '0 0 5px 10px transparent',
          },
        },
      },
      animationDelay: {  // Definisci i valori di delay personalizzati
        '100': '0.1s',
        '200': '0.2s',
        '500': '0.5s',
        '1000': '1s',
      },
      backgroundSize: {
        "300%": "300%",
      },
      backgroundImage: {
        hero: "url('/static/image/home-bg.jpg')", // Assicurati che il percorso sia corretto
      },
      borderRadius: {
        '2.5xl': '20px',
      },
      fontFamily: {
        body: ["Inter", "sans-serif"],
      },
      colors: {
        brand: {
          50: "#e6f1f7",
          100: "#b3d6ea",
          200: "#80bbdd",
          300: "#4da0d1",
          400: "#1a85c4",
          500: "#006398", // Colore principale
          600: "#005680",
          700: "#004968",
          800: "#003d50",
          900: "#003038",
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),

    // ✅ Plugin custom per generare .pulse-shadow-[color]
    plugin(function ({ matchUtilities, theme }) {
      const colors = flattenColorPalette(theme('colors'))

      matchUtilities(
        {
          'pulse-shadow': (value) => ({
            '--tw-shadow-color': value,
            animation: 'pulse-shadow-generic 2.5s infinite',
          }),
        },
        { values: colors, type: ['color'] }
      )
    }),
  ],
};