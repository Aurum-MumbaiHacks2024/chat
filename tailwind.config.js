/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './aurum/templates/**/*.html',
    './aurum/templates/*.html',
  ],
  theme: {
    extend: {
      colors: {
        surface_dark: '#2B4E41',
        neutral_dark: '#001109',
        accent_dark: '#B38D60',
        surface: '#0F3628',
        neutral: '#C5E0D3',
        accent: '#C48901',
      },
    },
  },
  plugins: [],
}

