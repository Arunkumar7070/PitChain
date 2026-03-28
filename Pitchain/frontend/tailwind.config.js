/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pitchain: {
          primary: '#6366f1',   // Indigo - main brand color
          secondary: '#f59e0b', // Amber - accent
          dark: '#0f172a',      // Slate 900 - dark bg
          card: '#1e293b',      // Slate 800 - card bg
          border: '#334155',    // Slate 700 - borders
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
