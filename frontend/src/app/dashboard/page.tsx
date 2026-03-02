'use client'

import useSWR from 'swr'
import { fetchPositions, fetchLogs } from '@/lib/api'
import { TopBar } from '@/components/layout/TopBar'
import { GlowCard } from '@/components/ui/GlowCard'
import { Badge, ActionBadge } from '@/components/ui/Badge'
import { LoadingState, ErrorState } from '@/components/ui/Spinner'
import type { AgentSession, Position } from '@/lib/types'
import { AGENT_CONFIG } from '@/lib/types'

// ── Stat Tile ──────────────────────────────────────────────
function StatTile({
  label,
  value,
  sub,
  accent,
  glow = false,
}: {
  label: string
  value: string
  sub?: string
  accent?: string
  glow?: boolean
}) {
  return (
    <GlowCard className="p-5" accent="none">
      <p className="font-mono text-[10px] tracking-[0.14em] text-[#4a6080]">{label}</p>
      <p
        className={`mt-2 font-mono text-2xl font-black tabular-nums ${glow ? 'text-glow-cyan' : ''}`}
        style={accent ? { color: accent } : { color: '#e8f4f8' }}
      >
        {value}
      </p>
      {sub && <p className="mt-1 font-mono text-[10px] tracking-wider text-[#4a6080]">{sub}</p>}
    </GlowCard>
  )
}

// ── Position Row ───────────────────────────────────────────
function PositionRow({ pos }: { pos: Position }) {
  const isLong = pos.side === 'LONG'

  return (
    <div className="flex items-center gap-4 rounded border border-[#1a2744] bg-[#0a0f1e] p-4 transition-all hover:border-[#1e3a6e]">
      {/* Side indicator */}
      <div
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded border font-mono text-xs font-bold ${
          isLong
            ? 'border-[#00ff88]/30 bg-[#00ff88]/10 text-[#00ff88]'
            : 'border-[#ff3366]/30 bg-[#ff3366]/10 text-[#ff3366]'
        }`}
      >
        {isLong ? 'L' : 'S'}
      </div>

      {/* Symbol + size */}
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-bold text-[#e8f4f8]">{pos.symbol}</span>
          <Badge color={isLong ? '#00ff88' : '#ff3366'}>{isLong ? 'LONG' : 'SHORT'}</Badge>
        </div>
        <p className="mt-0.5 font-mono text-xs text-[#4a6080]">
          {pos.size} contracts @ {pos.entry_price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
        </p>
      </div>

      {/* SL / TP */}
      <div className="hidden text-right md:block">
        <p className="font-mono text-[10px] tracking-wider text-[#4a6080]">SL / TP</p>
        <p className="mt-0.5 font-mono text-xs tabular-nums">
          <span className="text-[#ff3366]">{pos.stop_loss?.toFixed(1) ?? '—'}</span>
          <span className="mx-1 text-[#2a3a54]">/</span>
          <span className="text-[#00ff88]">{pos.take_profit?.toFixed(1) ?? '—'}</span>
        </p>
      </div>

      {/* Status */}
      <Badge color="#00ff88" dot>OPEN</Badge>
    </div>
  )
}

// ── Latest MAGI Decision Card ──────────────────────────────
function LatestDecision({ session }: { session: AgentSession }) {
  const decision = session.final_decision
  if (!decision) return null

  const action = decision.action.toUpperCase()
  const isLong = action === 'BUY'
  const isShort = action === 'SELL'
  const accentColor = isLong ? '#00ff88' : isShort ? '#ff3366' : '#8ba3c4'

  return (
    <GlowCard accent="gold" className="p-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] tracking-[0.14em] text-[#ffd60a]/60">MAGI</span>
          <span className="font-mono text-[10px] tracking-[0.14em] text-[#4a6080]">LATEST DECISION</span>
        </div>
        <span className="font-mono text-[10px] tracking-wider text-[#4a6080]">
          {new Date(session.created_at).toLocaleString('ja-JP', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      {/* Action + Confidence */}
      <div className="mt-4 flex items-end gap-4">
        <div>
          <p className="font-mono text-[10px] tracking-widest text-[#4a6080]">ACTION</p>
          <p className="mt-1 font-mono text-3xl font-black tracking-widest" style={{ color: accentColor }}>
            {action}
          </p>
        </div>
        <div className="flex-1 pb-1">
          <div className="flex items-center justify-between">
            <p className="font-mono text-[10px] tracking-widest text-[#4a6080]">CONFIDENCE</p>
            <p className="font-mono text-[10px] font-bold text-[#ffd60a]">
              {(decision.confidence * 100).toFixed(0)}%
            </p>
          </div>
          <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-[#1a2744]">
            <div
              className="h-full rounded-full bg-[#ffd60a] shadow-[0_0_8px_rgba(255,214,10,0.6)] transition-all duration-700"
              style={{ width: `${decision.confidence * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Reasoning snippet */}
      <p className="mt-4 line-clamp-3 font-mono text-xs leading-relaxed text-[#4a6080]">
        {decision.reasoning}
      </p>

      {/* Agent opinions summary */}
      <div className="mt-4 flex flex-wrap gap-2">
        {session.opinions.map((op) => {
          const cfg = AGENT_CONFIG[op.agent_name] ?? { label: op.agent_name, color: '#8ba3c4', abbr: '??' }
          return (
            <div
              key={op.id}
              className="flex items-center gap-1.5 rounded px-2 py-1"
              style={{ backgroundColor: cfg.color + '12', border: `1px solid ${cfg.color}30` }}
            >
              <span className="font-mono text-[9px] font-bold tracking-widest" style={{ color: cfg.color }}>
                {cfg.abbr}
              </span>
              <ActionBadge action={op.action} />
            </div>
          )
        })}
      </div>
    </GlowCard>
  )
}

// ── Page ──────────────────────────────────────────────────
export default function DashboardPage() {
  const {
    data: positions,
    error: posError,
    isLoading: posLoading,
  } = useSWR('/api/position', fetchPositions, { refreshInterval: 15000 })

  const {
    data: sessions,
    error: logError,
    isLoading: logLoading,
  } = useSWR('/api/logs?limit=1&offset=0', () => fetchLogs(1, 0), { refreshInterval: 60000 })

  const openPositions = positions ?? []
  const latestSession = sessions?.[0] ?? null
  const totalSize = openPositions.reduce((sum, p) => sum + p.size, 0)

  return (
    <div className="flex flex-col">
      <TopBar title="DASHBOARD" subtitle="REAL-TIME TRADING MONITOR" />

      <div className="space-y-6 p-6">
        {/* Stat tiles */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatTile
            label="OPEN POSITIONS"
            value={String(openPositions.length)}
            sub={`${totalSize.toFixed(3)} contracts total`}
            accent="#00e5ff"
            glow
          />
          <StatTile
            label="SYSTEM STATUS"
            value="ONLINE"
            sub="Scheduler running"
            accent="#00ff88"
          />
          <StatTile
            label="CYCLE INTERVAL"
            value="15 MIN"
            sub="AI analysis cycle"
            accent="#bf5af2"
          />
          <StatTile
            label="ACTIVE AGENTS"
            value="4"
            sub="Trend · Contrarian · Risk · Master"
            accent="#ffd60a"
          />
        </div>

        {/* Main content */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Positions */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h2 className="font-mono text-[10px] tracking-[0.14em] text-[#4a6080]">
                OPEN POSITIONS
              </h2>
              <span className="font-mono text-[10px] text-[#2a3a54]">AUTO-REFRESH 15s</span>
            </div>

            {posLoading && <LoadingState label="FETCHING POSITIONS..." />}
            {posError && <ErrorState message="Failed to fetch positions" />}
            {!posLoading && !posError && openPositions.length === 0 && (
              <GlowCard className="flex flex-col items-center justify-center py-12">
                <p className="font-mono text-xs tracking-widest text-[#2a3a54]">NO OPEN POSITIONS</p>
                <p className="mt-1 font-mono text-[10px] text-[#1a2744]">MARKET WATCHING...</p>
              </GlowCard>
            )}
            {openPositions.map((p) => (
              <PositionRow key={p.id} pos={p} />
            ))}
          </div>

          {/* Latest MAGI Decision */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h2 className="font-mono text-[10px] tracking-[0.14em] text-[#4a6080]">
                LATEST MAGI DECISION
              </h2>
              <span className="font-mono text-[10px] text-[#2a3a54]">AUTO-REFRESH 60s</span>
            </div>

            {logLoading && <LoadingState label="CONSULTING MAGI..." />}
            {logError && <ErrorState message="Failed to fetch MAGI logs" />}
            {!logLoading && !logError && !latestSession && (
              <GlowCard className="flex flex-col items-center justify-center py-12">
                <p className="font-mono text-xs tracking-widest text-[#2a3a54]">NO DATA YET</p>
                <p className="mt-1 font-mono text-[10px] text-[#1a2744]">AWAITING FIRST CYCLE...</p>
              </GlowCard>
            )}
            {latestSession && <LatestDecision session={latestSession} />}
          </div>
        </div>

        {/* Agent legend */}
        <GlowCard className="p-4">
          <p className="mb-3 font-mono text-[10px] tracking-[0.14em] text-[#4a6080]">MAGI AGENT SYSTEM</p>
          <div className="flex flex-wrap gap-4">
            {Object.entries(AGENT_CONFIG).map(([key, cfg]) => (
              <div key={key} className="flex items-center gap-2">
                <div
                  className="flex h-6 w-6 items-center justify-center rounded text-[9px] font-black"
                  style={{ backgroundColor: cfg.color + '20', color: cfg.color, border: `1px solid ${cfg.color}40` }}
                >
                  {cfg.abbr}
                </div>
                <span className="font-mono text-[10px] tracking-wider" style={{ color: cfg.color }}>
                  {cfg.label}
                </span>
              </div>
            ))}
          </div>
        </GlowCard>
      </div>
    </div>
  )
}
