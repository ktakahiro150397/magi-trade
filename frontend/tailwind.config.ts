import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // MAGI System color palette — near-future cyberpunk
        background: '#050810',
        surface: '#0a0f1e',
        panel: '#0d1428',
        border: '#1a2744',
        'border-bright': '#1e3a6e',

        // Neon accents
        cyan: {
          DEFAULT: '#00e5ff',
          dim: '#00b8cc',
          glow: 'rgba(0,229,255,0.15)',
        },
        purple: {
          DEFAULT: '#bf5af2',
          dim: '#9b44cc',
          glow: 'rgba(191,90,242,0.15)',
        },
        gold: {
          DEFAULT: '#ffd60a',
          dim: '#c9aa00',
          glow: 'rgba(255,214,10,0.15)',
        },
        orange: {
          DEFAULT: '#ff9f0a',
          dim: '#cc7f00',
          glow: 'rgba(255,159,10,0.15)',
        },

        // Signal colors
        gain: '#00ff88',
        loss: '#ff3366',
        'gain-dim': '#00cc6a',
        'loss-dim': '#cc1a4d',

        // Text
        'text-primary': '#e8f4f8',
        'text-secondary': '#8ba3c4',
        'text-muted': '#4a6080',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'neon-cyan': '0 0 20px rgba(0,229,255,0.3), 0 0 60px rgba(0,229,255,0.1)',
        'neon-purple': '0 0 20px rgba(191,90,242,0.3), 0 0 60px rgba(191,90,242,0.1)',
        'neon-gold': '0 0 20px rgba(255,214,10,0.3), 0 0 60px rgba(255,214,10,0.1)',
        'neon-gain': '0 0 20px rgba(0,255,136,0.3)',
        'neon-loss': '0 0 20px rgba(255,51,102,0.3)',
        'panel': '0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04)',
      },
      backgroundImage: {
        'grid-pattern': `linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
                         linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px)`,
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'scanline': 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px)',
      },
      backgroundSize: {
        'grid': '32px 32px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'scan': 'scan 8s linear infinite',
        'flicker': 'flicker 0.15s infinite',
      },
      keyframes: {
        glow: {
          '0%': { opacity: '0.6' },
          '100%': { opacity: '1' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        flicker: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.95' },
        },
      },
    },
  },
  plugins: [],
}

export default config
