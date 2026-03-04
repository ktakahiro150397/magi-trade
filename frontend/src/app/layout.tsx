import type { Metadata } from 'next'
import './globals.css'
import { Sidebar } from '@/components/layout/Sidebar'

export const metadata: Metadata = {
  title: 'MAGI Trade — AI Multi-Agent Trading System',
  description: 'Hyperliquid AI-Driven Multi-Agent Trading System Dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja" className="dark">
      <body className="flex h-screen overflow-hidden bg-[#050810]">
        {/*
          AUTH_PLACEHOLDER:
          Wrap this layout with a SessionProvider (next-auth) and add auth guard
          when Google authentication is implemented.
          Example:
            <SessionProvider session={session}>
              <AuthGuard>
                <Sidebar />
                ...
              </AuthGuard>
            </SessionProvider>
        */}
        <Sidebar />

        {/* Main content area */}
        <div className="relative flex flex-1 flex-col overflow-hidden">
          {/* Background grid */}
          <div className="pointer-events-none absolute inset-0 bg-grid opacity-100" />

          {/* Content */}
          <main className="relative flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
