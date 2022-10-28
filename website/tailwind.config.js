/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["site/Mophidian/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
}