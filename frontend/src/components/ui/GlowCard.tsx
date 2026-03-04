'use client'

import { clsx } from 'clsx'

interface GlowCardProps {
  children: React.ReactNode
  className?: string
  accent?: 'cyan' | 'purple' | 'gold' | 'orange' | 'gain' | 'loss' | 'none'
  hover?: boolean
}

const accentStyles: Record<string, string> = {
  cyan: 'border-cyan-500/30 hover:border-cyan-500/60 hover:shadow-neon-cyan',
  purple: 'border-purple-500/30 hover:border-purple-500/60 hover:shadow-neon-purple',
  gold: 'border-yellow-400/30 hover:border-yellow-400/60 hover:shadow-neon-gold',
  orange: 'border-orange-400/30 hover:border-orange-400/60',
  gain: 'border-green-400/30 hover:border-green-400/60 hover:shadow-neon-gain',
  loss: 'border-red-400/30 hover:border-red-400/60 hover:shadow-neon-loss',
  none: 'border-[#1a2744]',
}

export function GlowCard({ children, className, accent = 'none', hover = false }: GlowCardProps) {
  return (
    <div
      className={clsx(
        'relative rounded-lg border bg-[#0d1428] shadow-panel transition-all duration-300',
        accentStyles[accent],
        hover && 'cursor-pointer',
        className
      )}
    >
      {/* Subtle inner glow at top */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px rounded-t-lg bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      {children}
    </div>
  )
}
