import { clsx } from 'clsx'

interface BadgeProps {
  children: React.ReactNode
  color?: string
  className?: string
  dot?: boolean
}

export function Badge({ children, color, className, dot = false }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-sm px-2 py-0.5 font-mono text-xs font-bold tracking-widest uppercase',
        className
      )}
      style={
        color
          ? {
              color,
              backgroundColor: color + '18',
              border: `1px solid ${color}44`,
            }
          : undefined
      }
    >
      {dot && (
        <span
          className="h-1.5 w-1.5 rounded-full animate-pulse"
          style={{ backgroundColor: color ?? 'currentColor' }}
        />
      )}
      {children}
    </span>
  )
}

interface ActionBadgeProps {
  action: string
}

const ACTION_STYLES: Record<string, { label: string; color: string }> = {
  BUY: { label: 'LONG', color: '#00ff88' },
  SELL: { label: 'SHORT', color: '#ff3366' },
  HOLD: { label: 'HOLD', color: '#8ba3c4' },
  CLOSE: { label: 'CLOSE', color: '#ff9f0a' },
}

export function ActionBadge({ action }: ActionBadgeProps) {
  const cfg = ACTION_STYLES[action.toUpperCase()] ?? { label: action, color: '#8ba3c4' }
  return <Badge color={cfg.color}>{cfg.label}</Badge>
}
