'use client'

import { useEffect, useState } from 'react'
import useSWR from 'swr'
import { fetchHealth } from '@/lib/api'

interface TopBarProps {
  title: string
  subtitle?: string
}

export function TopBar({ title, subtitle }: TopBarProps) {
  const [time, setTime] = useState('')
  const { data: health } = useSWR('/health', fetchHealth, { refreshInterval: 30000 })

  useEffect(() => {
    const tick = () => {
      setTime(
        new Date().toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          timeZoneName: 'short',
        })
      )
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  const isOnline = health?.status === 'ok'

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-[#1a2744] bg-[#070c1a]/80 px-6 backdrop-blur-sm">
      {/* Page title */}
      <div>
        <h1 className="font-mono text-sm font-bold tracking-[0.15em] text-[#e8f4f8]">{title}</h1>
        {subtitle && (
          <p className="mt-0.5 font-mono text-[10px] tracking-widest text-[#4a6080]">{subtitle}</p>
        )}
      </div>

      {/* Right side status */}
      <div className="flex items-center gap-6">
        {/* API status */}
        <div className="flex items-center gap-2">
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              isOnline
                ? 'animate-pulse bg-[#00ff88] shadow-[0_0_6px_rgba(0,255,136,0.8)]'
                : 'bg-[#ff3366] shadow-[0_0_6px_rgba(255,51,102,0.8)]'
            }`}
          />
          <span className="font-mono text-[10px] tracking-widest text-[#4a6080]">
            API {isOnline ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>

        {/* Divider */}
        <div className="h-4 w-px bg-[#1a2744]" />

        {/* Clock */}
        <span className="font-mono text-xs tabular-nums text-[#4a6080]">{time}</span>
      </div>
    </header>
  )
}
