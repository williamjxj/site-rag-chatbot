import type { Config } from "tailwindcss";

/**
 * Tailwind CSS v4 Configuration
 * 
 * Note: In Tailwind v4, theme configuration is primarily done via CSS using @theme directive.
 * This config file is kept for content paths and any JS-based configuration needs.
 * Theme colors and other design tokens are defined in app/globals.css using CSS variables.
 */
const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  // Theme configuration moved to CSS (app/globals.css) for Tailwind v4
  // Colors and design tokens are defined via CSS variables in :root
};

export default config;
