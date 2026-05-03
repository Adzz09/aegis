/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Backgrounds
        'bg-deep':    'var(--color-bg-deep)',
        'bg-void':    'var(--color-bg-void)',
        'bg-abyss':   'var(--color-bg-abyss)',
        'bg-surface': 'var(--color-bg-surface)',
        'bg-overlay': 'var(--color-bg-overlay)',
        // Blues
        'blue': {
          dim:    'var(--color-blue-dim)',
          dark:   'var(--color-blue-dark)',
          core:   'var(--color-blue-core)',
          bright: 'var(--color-blue-bright)',
          glow:   'var(--color-blue-glow)',
          light:  'var(--color-blue-light)',
        },
        // Threat levels
        'threat': {
          0:       'var(--color-threat-0)',
          1:       'var(--color-threat-1)',
          2:       'var(--color-threat-2)',
          3:       'var(--color-threat-3)',
          4:       'var(--color-threat-4)',
          engaged: 'var(--color-threat-engaged)',
          dead:    'var(--color-threat-dead)',
        },
        // Radar green
        'radar': {
          dark:   'var(--color-radar-dark)',
          core:   'var(--color-radar-core)',
          bright: 'var(--color-radar-bright)',
          glow:   'var(--color-radar-glow)',
        },
        // Text
        'text': {
          primary:   'var(--color-text-primary)',
          secondary: 'var(--color-text-secondary)',
          muted:     'var(--color-text-muted)',
          disabled:  'var(--color-text-disabled)',
          accent:    'var(--color-text-accent)',
        }
      },
      fontFamily: {
        mono:  ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans:  ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-red':    'pulse-red 1.5s ease-in-out infinite',
        'pulse-fast':   'pulse-red 0.6s ease-in-out infinite',
        'radar-expand': 'expand-fade 2s ease-out infinite',
        'row-pulse':    'row-pulse 1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
