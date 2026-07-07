import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        paper: '#FAF7F2',
        'paper-warm': '#F5F0E8',
        ink: '#2C2C2C',
        'ink-light': '#6B6B6B',
        'ink-faint': '#B8B2A6',
        vermillion: '#C43A31',
        'vermillion-light': '#E8A090',
      },
      fontFamily: {
        serif: ['Noto Serif SC', 'serif'],
        sans: ['Noto Sans SC', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config