/** Build: npx tailwindcss@3 -c tailwind.config.js -i app/static/css/src.css -o app/static/css/app.css --minify */
module.exports = {
  content: ["./app/templates/**/*.html", "./app/static/js/*.js"],
  theme: {
    extend: {
      colors: {
        navy: { DEFAULT: "#0A192F", 900: "#06101f", 800: "#0d2038", 700: "#13304f" },
        cyan: { DEFAULT: "#00D4FF" },
        ghost: "#bfe9f5",
      },
      fontFamily: {
        display: ["Iowan Old Style", "Palatino Linotype", "Palatino", "Georgia", "serif"],
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
      },
    },
  },
};
