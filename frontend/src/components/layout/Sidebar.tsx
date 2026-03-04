'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'

const NAV_ITEMS = [
  {
    href: '/dashboard',
    label: 'DASHBOARD',
    abbr: '01',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth={1.5}>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </svg>
    ),
  },
  {
    href: '/logs',
    label: 'MAGI LOGS',
    abbr: '02',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth={1.5}>
        <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    href: '/history',
    label: 'HISTORY',
    abbr: '03',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth={1.5}>
        <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    href: '/settings',
    label: 'SETTINGS',
    abbr: '04',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth={1.5}>
        <path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex h-screen w-[220px] shrink-0 flex-col border-r border-[#1a2744] bg-[#070c1a]">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-[#1a2744] px-5">
        <div className="flex items-baseline gap-2">
          <span className="font-mono text-xl font-black tracking-[0.15em] text-[#00e5ff] drop-shadow-[0_0_12px_rgba(0,229,255,0.8)]">
            MAGI
          </span>
          <span className="font-mono text-xs tracking-widest text-[#4a6080]">TRADE</span>
        </div>
      </div>

      {/* System status indicator */}
      <div className="flex items-center gap-2 border-b border-[#1a2744] px-5 py-3">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#00ff88] shadow-[0_0_6px_rgba(0,255,136,0.8)]" />
        <span className="font-mono text-[10px] tracking-widest text-[#4a6080]">SYSTEM ONLINE</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'group flex items-center gap-3 rounded px-3 py-2.5 transition-all duration-200',
                isActive
                  ? 'bg-[#00e5ff]/10 text-[#00e5ff]'
                  : 'text-[#4a6080] hover:bg-[#1a2744]/50 hover:text-[#8ba3c4]'
              )}
            >
              <span
                className={clsx(
                  'font-mono text-[10px] tracking-widest transition-colors',
                  isActive ? 'text-[#00e5ff]/60' : 'text-[#2a3a54] group-hover:text-[#4a6080]'
                )}
              >
                {item.abbr}
              </span>
              <span className={clsx('transition-colors', isActive ? 'text-[#00e5ff]' : '')}>
                {item.icon}
              </span>
              <span
                className={clsx(
                  'font-mono text-[11px] tracking-[0.12em]',
                  isActive ? 'font-bold' : 'font-medium'
                )}
              >
                {item.label}
              </span>
              {isActive && (
                <span className="ml-auto h-4 w-0.5 rounded-full bg-[#00e5ff] shadow-[0_0_6px_rgba(0,229,255,0.8)]" />
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer — placeholder for future Google auth */}
      <div className="border-t border-[#1a2744] px-4 py-4">
        {/* AUTH_PLACEHOLDER: Replace this section with Google Sign-In when auth is added */}
        <div className="flex items-center gap-3 rounded px-2 py-2 opacity-40">
          <div className="flex h-7 w-7 items-center justify-center rounded-full border border-[#1a2744] bg-[#0d1428]">
            <svg viewBox="0 0 24 24" fill="currentColor" className="h-3.5 w-3.5 text-[#4a6080]">
              <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
            </svg>
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="truncate font-mono text-[10px] tracking-wider text-[#4a6080]">GUEST USER</p>
            <p className="font-mono text-[9px] tracking-wider text-[#2a3a54]">AUTH PENDING</p>
          </div>
        </div>

        <p className="mt-3 px-2 font-mono text-[9px] tracking-widest text-[#2a3a54]">
          v0.1.0 — MAGI SYSTEM
        </p>
      </div>
    </aside>
  )
}
