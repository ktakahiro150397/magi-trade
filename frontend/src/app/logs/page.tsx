'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { fetchLogs } from '@/lib/api'
import { TopBar } from '@/components/layout/TopBar'
import { GlowCard } from '@/components/ui/GlowCard'
import { Badge, ActionBadge } from '@/components/ui/Badge'
import { LoadingState, ErrorState } from '@/components/ui/Spinner'
import type { AgentSession, AgentOpinion } from '@/lib/types'
import { AGENT_CONFIG } from '@/lib/types'

// ── Opinion Bubble ─────────────────────────────────────────
function OpinionBubble({ opinion, isMaster }: { opinion: AgentOpinion; isMaster: boolean }) {
  const cfg = AGENT_CONFIG[opinion.agent_name] ?? {
    label: opinion.agent_name,
    color: '#8ba3c4',
    glow: 'rgba(139,163,196,0.1)',
    abbr: '??',
  }
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={`flex gap-3 ${isMaster ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className="flex flex-col items-center gap-1">
        <div
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-sm font-mono text-[11px] font-black"
          style={{
            backgroundColor: cfg.color + '18',
            color: cfg.color,
            border: `1px solid ${cfg.color}40`,
            boxShadow: `0 0 12px ${cfg.glow}`,
          }}
        >
          {cfg.abbr}
        </div>
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[80%] rounded-lg p-3 ${isMaster ? 'rounded-tr-none' : 'rounded-tl-none'}`}
        style={{
          backgroundColor: isMaster ? cfg.color + '12' : '#0d1428',
          border: `1px solid ${cfg.color}${isMaster ? '40' : '20'}`,
          boxShadow: isMaster ? `0 0 24px ${cfg.glow}` : undefined,
        }}
      >
        {/* Header */}
        <div className="mb-2 flex items-center gap-2">
          <span className="font-mono text-[10px] font-bold tracking-widest" style={{ color: cfg.color }}>
            {cfg.label}
          </span>
          <ActionBadge action={opinion.action} />
          <span className="ml-auto font-mono text-[10px] text-[#4a6080]">
            {(opinion.confidence * 100).toFixed(0)}% conf.
          </span>
        </div>

        {/* Confidence bar */}
        <div className="mb-2 h-0.5 w-full overflow-hidden rounded-full bg-[#1a2744]">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${opinion.confidence * 100}%`,
              backgroundColor: cfg.color,
              boxShadow: `0 0 4px ${cfg.color}`,
            }}
          />
        </div>

        {/* Reasoning */}
        <p
          className={`font-mono text-xs leading-relaxed text-[#8ba3c4] ${!expanded ? 'line-clamp-3' : ''}`}
        >
          {opinion.reasoning}
        </p>
        {opinion.reasoning.length > 200 && (
          <button
            onClick={() => setExpanded((v) => !v)}
            className="mt-1 font-mono text-[10px] tracking-wider transition-colors hover:text-[#e8f4f8]"
            style={{ color: cfg.color + 'aa' }}
          >
            {expanded ? '▲ COLLAPSE' : '▼ EXPAND'}
          </button>
        )}
      </div>
    </div>
  )
}

// ── Session Card ──────────────────────────────────────────
function SessionCard({ session, index }: { session: AgentSession; index: number }) {
  const [open, setOpen] = useState(index === 0)
  const decision = session.final_decision

  const decisionAction = decision?.action.toUpperCase()
  const isLong = decisionAction === 'BUY'
  const isShort = decisionAction === 'SELL'
  const accentColor = isLong ? '#00ff88' : isShort ? '#ff3366' : '#8ba3c4'

  const allOpinions = [
    ...session.opinions.filter((o) => o.agent_name !== 'MasterAgent'),
    ...(decision
      ? [
          {
            id: decision.id,
            agent_name: 'MasterAgent',
            action: decision.action,
            confidence: decision.confidence,
            reasoning: decision.reasoning,
            created_at: decision.created_at,
          } as AgentOpinion,
        ]
      : []),
  ]

  return (
    <GlowCard accent={decision ? 'none' : 'none'} className="overflow-hidden">
      {/* Session header */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-4 p-4 text-left transition-colors hover:bg-[#0a0f1e]"
      >
        {/* Index */}
        <span className="font-mono text-[10px] tracking-widest text-[#2a3a54]">
          #{String(index + 1).padStart(3, '0')}
        </span>

        {/* Datetime */}
        <span className="font-mono text-xs tabular-nums text-[#4a6080]">
          {new Date(session.created_at).toLocaleString('ja-JP')}
        </span>

        {/* Decision badge */}
        {decision ? (
          <div className="flex items-center gap-2">
            <Badge color={accentColor}>{decisionAction}</Badge>
            <span className="font-mono text-[10px] text-[#4a6080]">
              {(decision.confidence * 100).toFixed(0)}%
            </span>
          </div>
        ) : (
          <Badge color="#4a6080">NO DECISION</Badge>
        )}

        {/* Opinion count */}
        <span className="ml-auto font-mono text-[10px] tracking-wider text-[#2a3a54]">
          {session.opinions.length} AGENTS
        </span>

        {/* Chevron */}
        <span
          className={`font-mono text-[10px] text-[#4a6080] transition-transform ${open ? 'rotate-180' : ''}`}
        >
          ▼
        </span>
      </button>

      {/* Expanded discussion */}
      {open && (
        <div className="border-t border-[#1a2744] p-4">
          <div className="space-y-4">
            {allOpinions.map((op) => (
              <OpinionBubble
                key={`${op.agent_name}-${op.id}`}
                opinion={op}
                isMaster={op.agent_name === 'MasterAgent'}
              />
            ))}
            {allOpinions.length === 0 && (
              <p className="py-4 text-center font-mono text-xs text-[#2a3a54]">NO OPINIONS RECORDED</p>
            )}
          </div>
        </div>
      )}
    </GlowCard>
  )
}

// ── Page ──────────────────────────────────────────────────
export default function LogsPage() {
  const [offset, setOffset] = useState(0)
  const limit = 10

  const { data: sessions, error, isLoading } = useSWR(
    `/api/logs?limit=${limit}&offset=${offset}`,
    () => fetchLogs(limit, offset),
    { refreshInterval: 60000 }
  )

  return (
    <div className="flex flex-col">
      <TopBar title="MAGI LOGS" subtitle="AI AGENT DISCUSSION VIEWER" />

      <div className="space-y-4 p-6">
        {/* Header info */}
        <div className="flex items-center justify-between">
          <p className="font-mono text-[10px] tracking-widest text-[#4a6080]">
            SHOWING SESSION {offset + 1}–{offset + limit} · AUTO-REFRESH 60s
          </p>
          <div className="flex items-center gap-2">
            {Object.entries(AGENT_CONFIG).map(([, cfg]) => (
              <div
                key={cfg.abbr}
                className="flex h-5 w-5 items-center justify-center rounded-sm font-mono text-[8px] font-bold"
                title={cfg.label}
                style={{ backgroundColor: cfg.color + '18', color: cfg.color, border: `1px solid ${cfg.color}30` }}
              >
                {cfg.abbr}
              </div>
            ))}
          </div>
        </div>

        {isLoading && <LoadingState label="CONSULTING MAGI SYSTEM..." />}
        {error && <ErrorState message="Failed to fetch discussion logs" />}

        {!isLoading && !error && (
          <>
            <div className="space-y-3">
              {sessions?.map((session, i) => (
                <SessionCard key={session.id} session={session} index={offset + i} />
              ))}
              {sessions?.length === 0 && (
                <GlowCard className="flex flex-col items-center justify-center py-16">
                  <p className="font-mono text-xs tracking-widest text-[#2a3a54]">NO SESSIONS YET</p>
                  <p className="mt-1 font-mono text-[10px] text-[#1a2744]">
                    MAGI SYSTEM AWAITING FIRST CYCLE
                  </p>
                </GlowCard>
              )}
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
                className="rounded border border-[#1a2744] px-4 py-2 font-mono text-[10px] tracking-widest text-[#4a6080] transition-all hover:border-[#1e3a6e] hover:text-[#8ba3c4] disabled:cursor-not-allowed disabled:opacity-30"
              >
                ◀ PREV
              </button>
              <span className="font-mono text-[10px] text-[#2a3a54]">
                {offset / limit + 1}
              </span>
              <button
                onClick={() => setOffset(offset + limit)}
                disabled={(sessions?.length ?? 0) < limit}
                className="rounded border border-[#1a2744] px-4 py-2 font-mono text-[10px] tracking-widest text-[#4a6080] transition-all hover:border-[#1e3a6e] hover:text-[#8ba3c4] disabled:cursor-not-allowed disabled:opacity-30"
              >
                NEXT ▶
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
