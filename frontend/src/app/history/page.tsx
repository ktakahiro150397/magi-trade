'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { fetchHistory } from '@/lib/api'
import { TopBar } from '@/components/layout/TopBar'
import { GlowCard } from '@/components/ui/GlowCard'
import { Badge } from '@/components/ui/Badge'
import { LoadingState, ErrorState } from '@/components/ui/Spinner'
import type { Trade } from '@/lib/types'

function PnlCell({ pnl }: { pnl: number | null }) {
  if (pnl === null) return <span className="text-[#4a6080]">—</span>
  const pos = pnl >= 0
  return (
    <span
      className={`font-bold tabular-nums ${pos ? 'text-[#00ff88]' : 'text-[#ff3366]'}`}
      style={{ textShadow: pos ? '0 0 8px rgba(0,255,136,0.4)' : '0 0 8px rgba(255,51,102,0.4)' }}
    >
      {pos ? '+' : ''}
      {pnl.toFixed(2)} USD
    </span>
  )
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { color: string; label: string }> = {
    OPEN: { color: '#00ff88', label: 'OPEN' },
    CLOSED: { color: '#4a6080', label: 'CLOSED' },
    CANCELLED: { color: '#ff9f0a', label: 'CANCELLED' },
    LIQUIDATED: { color: '#ff3366', label: 'LIQUIDATED' },
  }
  const cfg = map[status.toUpperCase()] ?? { color: '#8ba3c4', label: status }
  return <Badge color={cfg.color}>{cfg.label}</Badge>
}

function TradeRow({ trade }: { trade: Trade }) {
  const isLong = trade.side.toUpperCase() === 'LONG' || trade.side.toUpperCase() === 'BUY'

  return (
    <tr className="border-b border-[#1a2744] transition-colors hover:bg-[#00e5ff]/[0.02]">
      <td className="px-4 py-3">
        <span className="font-mono text-xs text-[#4a6080]">#{trade.id}</span>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <span
            className={`font-mono text-[10px] font-bold ${isLong ? 'text-[#00ff88]' : 'text-[#ff3366]'}`}
          >
            {isLong ? '▲' : '▼'}
          </span>
          <span className="font-mono text-sm font-bold text-[#e8f4f8]">{trade.symbol}</span>
        </div>
      </td>
      <td className="px-4 py-3">
        <Badge color={isLong ? '#00ff88' : '#ff3366'}>{isLong ? 'LONG' : 'SHORT'}</Badge>
      </td>
      <td className="px-4 py-3">
        <span className="font-mono text-xs tabular-nums text-[#8ba3c4]">{trade.size}</span>
      </td>
      <td className="px-4 py-3">
        <span className="font-mono text-xs tabular-nums text-[#8ba3c4]">
          ${trade.entry_price.toLocaleString()}
        </span>
      </td>
      <td className="px-4 py-3">
        <span className="font-mono text-xs tabular-nums text-[#8ba3c4]">
          {trade.exit_price ? `$${trade.exit_price.toLocaleString()}` : '—'}
        </span>
      </td>
      <td className="px-4 py-3">
        <PnlCell pnl={trade.pnl} />
      </td>
      <td className="px-4 py-3">
        <StatusBadge status={trade.status} />
      </td>
      <td className="px-4 py-3">
        <span className="font-mono text-[10px] tabular-nums text-[#4a6080]">
          {new Date(trade.created_at).toLocaleString('ja-JP', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </td>
    </tr>
  )
}

const STATUS_FILTERS = ['ALL', 'OPEN', 'CLOSED', 'CANCELLED']

export default function HistoryPage() {
  const [statusFilter, setStatusFilter] = useState<string>('ALL')
  const [offset, setOffset] = useState(0)
  const limit = 50

  const swrKey = `/api/history?limit=${limit}&offset=${offset}&status=${statusFilter}`
  const { data: trades, error, isLoading } = useSWR(swrKey, () =>
    fetchHistory(limit, offset, statusFilter === 'ALL' ? undefined : statusFilter)
  )

  // Summary stats
  const closedTrades = trades?.filter((t) => t.status === 'CLOSED') ?? []
  const totalPnl = closedTrades.reduce((sum, t) => sum + (t.pnl ?? 0), 0)
  const winCount = closedTrades.filter((t) => (t.pnl ?? 0) > 0).length
  const winRate = closedTrades.length > 0 ? (winCount / closedTrades.length) * 100 : 0

  return (
    <div className="flex flex-col">
      <TopBar title="TRADE HISTORY" subtitle="EXECUTION RECORD" />

      <div className="space-y-4 p-6">
        {/* Summary tiles */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <GlowCard className="p-4">
            <p className="font-mono text-[10px] tracking-widest text-[#4a6080]">TOTAL P&L</p>
            <p
              className={`mt-2 font-mono text-xl font-black tabular-nums ${
                totalPnl >= 0 ? 'text-[#00ff88] text-glow-gain' : 'text-[#ff3366] text-glow-loss'
              }`}
            >
              {totalPnl >= 0 ? '+' : ''}
              {totalPnl.toFixed(2)}
            </p>
            <p className="mt-0.5 font-mono text-[10px] text-[#2a3a54]">USD (closed only)</p>
          </GlowCard>

          <GlowCard className="p-4">
            <p className="font-mono text-[10px] tracking-widest text-[#4a6080]">WIN RATE</p>
            <p className="mt-2 font-mono text-xl font-black tabular-nums text-[#00e5ff]">
              {winRate.toFixed(1)}%
            </p>
            <p className="mt-0.5 font-mono text-[10px] text-[#2a3a54]">
              {winCount} / {closedTrades.length} trades
            </p>
          </GlowCard>

          <GlowCard className="p-4">
            <p className="font-mono text-[10px] tracking-widest text-[#4a6080]">DISPLAYED</p>
            <p className="mt-2 font-mono text-xl font-black tabular-nums text-[#e8f4f8]">
              {trades?.length ?? '—'}
            </p>
            <p className="mt-0.5 font-mono text-[10px] text-[#2a3a54]">records shown</p>
          </GlowCard>

          <GlowCard className="p-4">
            <p className="font-mono text-[10px] tracking-widest text-[#4a6080]">FILTER</p>
            <p className="mt-2 font-mono text-xl font-black tracking-wider text-[#bf5af2]">
              {statusFilter}
            </p>
            <p className="mt-0.5 font-mono text-[10px] text-[#2a3a54]">status filter</p>
          </GlowCard>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-1">
          {STATUS_FILTERS.map((s) => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setOffset(0) }}
              className={`rounded px-3 py-1.5 font-mono text-[10px] tracking-[0.12em] transition-all ${
                statusFilter === s
                  ? 'bg-[#00e5ff]/10 text-[#00e5ff] border border-[#00e5ff]/30'
                  : 'border border-[#1a2744] text-[#4a6080] hover:border-[#1e3a6e] hover:text-[#8ba3c4]'
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Table */}
        <GlowCard className="overflow-hidden">
          {isLoading && <LoadingState label="FETCHING TRADE HISTORY..." />}
          {error && <ErrorState message="Failed to fetch trade history" />}
          {!isLoading && !error && (
            <div className="overflow-x-auto">
              <table className="data-table w-full">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>SYMBOL</th>
                    <th>SIDE</th>
                    <th>SIZE</th>
                    <th>ENTRY</th>
                    <th>EXIT</th>
                    <th>P&L</th>
                    <th>STATUS</th>
                    <th>OPENED</th>
                  </tr>
                </thead>
                <tbody>
                  {trades?.map((t) => <TradeRow key={t.id} trade={t} />)}
                  {trades?.length === 0 && (
                    <tr>
                      <td colSpan={9} className="py-12 text-center font-mono text-xs text-[#2a3a54]">
                        NO TRADES FOUND
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </GlowCard>

        {/* Pagination */}
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="rounded border border-[#1a2744] px-4 py-2 font-mono text-[10px] tracking-widest text-[#4a6080] transition-all hover:border-[#1e3a6e] hover:text-[#8ba3c4] disabled:cursor-not-allowed disabled:opacity-30"
          >
            ◀ PREV
          </button>
          <span className="font-mono text-[10px] text-[#2a3a54]">PAGE {offset / limit + 1}</span>
          <button
            onClick={() => setOffset(offset + limit)}
            disabled={(trades?.length ?? 0) < limit}
            className="rounded border border-[#1a2744] px-4 py-2 font-mono text-[10px] tracking-widest text-[#4a6080] transition-all hover:border-[#1e3a6e] hover:text-[#8ba3c4] disabled:cursor-not-allowed disabled:opacity-30"
          >
            NEXT ▶
          </button>
        </div>
      </div>
    </div>
  )
}
