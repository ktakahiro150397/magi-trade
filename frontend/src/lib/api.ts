import type { AgentSession, Position, Trade, TradeSetting, TradeSettingUpdate } from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

async function fetcher<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

// ---- Position ----
export const fetchPositions = (): Promise<Position[]> =>
  fetcher<Position[]>('/api/position')

// ---- Logs ----
export const fetchLogs = (limit = 20, offset = 0): Promise<AgentSession[]> =>
  fetcher<AgentSession[]>(`/api/logs?limit=${limit}&offset=${offset}`)

// ---- History ----
export const fetchHistory = (limit = 50, offset = 0, status?: string): Promise<Trade[]> =>
  fetcher<Trade[]>(
    `/api/history?limit=${limit}&offset=${offset}${status ? `&status=${status}` : ''}`
  )

// ---- Settings ----
export const fetchSettings = (): Promise<TradeSetting> =>
  fetcher<TradeSetting>('/api/settings')

export const updateSettings = (body: TradeSettingUpdate): Promise<TradeSetting> =>
  fetcher<TradeSetting>('/api/settings', {
    method: 'PUT',
    body: JSON.stringify(body),
  })

// ---- Health ----
export const fetchHealth = (): Promise<{ status: string }> =>
  fetcher<{ status: string }>('/health')

// ---- SWR key factories ----
export const swrKeys = {
  positions: '/api/position',
  logs: (limit: number, offset: number) => `/api/logs?limit=${limit}&offset=${offset}`,
  history: (limit: number, offset: number, status?: string) =>
    `/api/history?limit=${limit}&offset=${offset}${status ? `&status=${status}` : ''}`,
  settings: '/api/settings',
  health: '/health',
}
