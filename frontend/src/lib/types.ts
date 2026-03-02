// ============================================================
// API Response Types — matching FastAPI schemas
// ============================================================

export interface Position {
  id: number
  symbol: string
  side: 'LONG' | 'SHORT'
  size: number
  entry_price: number
  stop_loss: number | null
  take_profit: number | null
  status: string
}

export interface AgentOpinion {
  id: number
  agent_name: string
  action: string
  confidence: number
  reasoning: string
  created_at: string
}

export interface FinalDecision {
  id: number
  action: string
  confidence: number
  reasoning: string
  created_at: string
}

export interface AgentSession {
  id: number
  created_at: string
  opinions: AgentOpinion[]
  final_decision: FinalDecision | null
}

export interface Trade {
  id: number
  session_id: number | null
  symbol: string
  side: string
  size: number
  entry_price: number
  exit_price: number | null
  stop_loss: number | null
  take_profit: number | null
  pnl: number | null
  status: string
  created_at: string
  closed_at: string | null
}

export interface TradeSetting {
  id: number
  risk_percent: number
  leverage: number
  max_hold_hours: number
  updated_at: string
}

export interface TradeSettingUpdate {
  risk_percent: number
  leverage: number
  max_hold_hours: number
}

// ============================================================
// Agent metadata
// ============================================================

export type AgentName = 'TrendAgent' | 'ContrarianAgent' | 'RiskAgent' | 'MasterAgent'

export const AGENT_CONFIG: Record<string, { label: string; color: string; glow: string; abbr: string }> = {
  TrendAgent: {
    label: 'TREND',
    color: '#00e5ff',
    glow: 'rgba(0,229,255,0.2)',
    abbr: 'TR',
  },
  ContrarianAgent: {
    label: 'CONTRARIAN',
    color: '#bf5af2',
    glow: 'rgba(191,90,242,0.2)',
    abbr: 'CT',
  },
  RiskAgent: {
    label: 'RISK',
    color: '#ff9f0a',
    glow: 'rgba(255,159,10,0.2)',
    abbr: 'RK',
  },
  MasterAgent: {
    label: 'MASTER',
    color: '#ffd60a',
    glow: 'rgba(255,214,10,0.2)',
    abbr: 'MA',
  },
}

export const ACTION_CONFIG: Record<string, { label: string; color: string }> = {
  BUY: { label: 'LONG', color: '#00ff88' },
  SELL: { label: 'SHORT', color: '#ff3366' },
  HOLD: { label: 'HOLD', color: '#8ba3c4' },
  CLOSE: { label: 'CLOSE', color: '#ff9f0a' },
}
