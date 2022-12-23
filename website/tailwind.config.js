/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [".dist/Mophidian/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
}