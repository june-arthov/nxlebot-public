/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx,html}", "./index.html"],
  theme: {
    extend: {
      colors: {
        primary: "#1e293b",
        accent: "#3b82f6",
      },
    },
  },
  plugins: [],
};
