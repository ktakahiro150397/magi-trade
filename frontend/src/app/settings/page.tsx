'use client'

import { useEffect, useState } from 'react'
import useSWR from 'swr'
import { fetchSettings, updateSettings } from '@/lib/api'
import { TopBar } from '@/components/layout/TopBar'
import { GlowCard } from '@/components/ui/GlowCard'
import { LoadingState, ErrorState } from '@/components/ui/Spinner'
import type { TradeSettingUpdate } from '@/lib/types'

interface RangeFieldProps {
  label: string
  description: string
  value: number
  min: number
  max: number
  step: number
  unit: string
  accentColor: string
  onChange: (v: number) => void
  warning?: string
}

function RangeField({
  label,
  description,
  value,
  min,
  max,
  step,
  unit,
  accentColor,
  onChange,
  warning,
}: RangeFieldProps) {
  const pct = ((value - min) / (max - min)) * 100

  return (
    <div className="space-y-3">
      <div className="flex items-baseline justify-between">
        <div>
          <p className="font-mono text-xs font-bold tracking-[0.12em] text-[#e8f4f8]">{label}</p>
          <p className="mt-0.5 font-mono text-[10px] text-[#4a6080]">{description}</p>
        </div>
        <div className="text-right">
          <span
            className="font-mono text-2xl font-black tabular-nums"
            style={{ color: accentColor }}
          >
            {value}
          </span>
          <span className="ml-1 font-mono text-[10px] text-[#4a6080]">{unit}</span>
        </div>
      </div>

      {/* Custom range slider */}
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full appearance-none"
          style={
            {
              '--accent': accentColor,
              height: '4px',
              background: `linear-gradient(to right, ${accentColor} ${pct}%, #1a2744 ${pct}%)`,
              outline: 'none',
              borderRadius: '2px',
            } as React.CSSProperties
          }
        />
      </div>

      {/* Min/Max labels */}
      <div className="flex justify-between">
        <span className="font-mono text-[9px] text-[#2a3a54]">
          {min} {unit}
        </span>
        <span className="font-mono text-[9px] text-[#2a3a54]">
          {max} {unit}
        </span>
      </div>

      {/* Warning */}
      {warning && (
        <p className="font-mono text-[10px] tracking-wider text-[#ff9f0a]">
          ⚠ {warning}
        </p>
      )}
    </div>
  )
}

function NumberField({
  label,
  description,
  value,
  min,
  max,
  unit,
  accentColor,
  onChange,
}: Omit<RangeFieldProps, 'step' | 'warning'>) {
  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between">
        <div>
          <p className="font-mono text-xs font-bold tracking-[0.12em] text-[#e8f4f8]">{label}</p>
          <p className="mt-0.5 font-mono text-[10px] text-[#4a6080]">{description}</p>
        </div>
        <span className="font-mono text-[10px] text-[#4a6080]">
          {min}–{max} {unit}
        </span>
      </div>
      <div
        className="flex items-center gap-2 rounded border px-3 py-2 transition-all focus-within:border-opacity-60"
        style={{ borderColor: accentColor + '30', backgroundColor: accentColor + '08' }}
      >
        <input
          type="number"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="flex-1 bg-transparent font-mono text-sm font-bold tabular-nums outline-none"
          style={{ color: accentColor }}
        />
        <span className="font-mono text-[10px] text-[#4a6080]">{unit}</span>
      </div>
    </div>
  )
}

export default function SettingsPage() {
  const { data: settings, error, isLoading, mutate } = useSWR('/api/settings', fetchSettings)

  const [form, setForm] = useState<TradeSettingUpdate>({
    risk_percent: 1,
    leverage: 5,
    max_hold_hours: 48,
  })
  const [saving, setSaving] = useState(false)
  const [saveResult, setSaveResult] = useState<'success' | 'error' | null>(null)
  const [isDirty, setIsDirty] = useState(false)

  useEffect(() => {
    if (settings) {
      setForm({
        risk_percent: settings.risk_percent,
        leverage: settings.leverage,
        max_hold_hours: settings.max_hold_hours,
      })
    }
  }, [settings])

  const update = <K extends keyof TradeSettingUpdate>(key: K, value: TradeSettingUpdate[K]) => {
    setForm((f) => ({ ...f, [key]: value }))
    setIsDirty(true)
    setSaveResult(null)
  }

  const handleSave = async () => {
    setSaving(true)
    setSaveResult(null)
    try {
      await updateSettings(form)
      await mutate()
      setSaveResult('success')
      setIsDirty(false)
    } catch {
      setSaveResult('error')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    if (settings) {
      setForm({
        risk_percent: settings.risk_percent,
        leverage: settings.leverage,
        max_hold_hours: settings.max_hold_hours,
      })
      setIsDirty(false)
      setSaveResult(null)
    }
  }

  return (
    <div className="flex flex-col">
      <TopBar title="SETTINGS" subtitle="RISK MANAGEMENT CONFIGURATION" />

      <div className="p-6">
        {isLoading && <LoadingState label="LOADING CONFIGURATION..." />}
        {error && <ErrorState message="Failed to load settings" />}

        {!isLoading && !error && (
          <div className="mx-auto max-w-2xl space-y-6">
            {/* Warning banner */}
            <GlowCard className="border-[#ff9f0a]/20 p-4">
              <div className="flex items-start gap-3">
                <span className="mt-0.5 font-mono text-sm text-[#ff9f0a]">⚠</span>
                <p className="font-mono text-[10px] leading-relaxed tracking-wider text-[#ff9f0a]/80">
                  RISK PARAMETERS DIRECTLY AFFECT POSITION SIZING AND LOSS EXPOSURE.
                  MODIFY WITH CAUTION. ALL CHANGES ARE APPLIED TO THE NEXT TRADING CYCLE.
                </p>
              </div>
            </GlowCard>

            {/* Settings form */}
            <GlowCard className="divide-y divide-[#1a2744]">
              {/* Section header */}
              <div className="px-6 py-4">
                <h2 className="font-mono text-[10px] font-bold tracking-[0.16em] text-[#00e5ff]">
                  RISK PARAMETERS
                </h2>
              </div>

              {/* Risk percent */}
              <div className="px-6 py-5">
                <RangeField
                  label="RISK PER TRADE"
                  description="Percentage of account equity to risk on each position"
                  value={form.risk_percent}
                  min={0.1}
                  max={10}
                  step={0.1}
                  unit="%"
                  accentColor="#00e5ff"
                  onChange={(v) => update('risk_percent', v)}
                  warning={form.risk_percent > 3 ? 'High risk threshold — ensure proper testing on testnet first' : undefined}
                />
              </div>

              {/* Leverage */}
              <div className="px-6 py-5">
                <RangeField
                  label="LEVERAGE"
                  description="Position size multiplier applied to all trades"
                  value={form.leverage}
                  min={1}
                  max={50}
                  step={1}
                  unit="×"
                  accentColor="#bf5af2"
                  onChange={(v) => update('leverage', v)}
                  warning={form.leverage > 20 ? 'Extreme leverage — liquidation risk significantly elevated' : undefined}
                />
              </div>

              {/* Max hold hours */}
              <div className="px-6 py-5">
                <NumberField
                  label="MAX HOLD DURATION"
                  description="Force-close open positions after this many hours"
                  value={form.max_hold_hours}
                  min={1}
                  max={720}
                  unit="hours"
                  accentColor="#ffd60a"
                  onChange={(v) => update('max_hold_hours', v)}
                />
              </div>
            </GlowCard>

            {/* Current saved values */}
            {settings && (
              <GlowCard className="p-4">
                <p className="mb-3 font-mono text-[10px] tracking-[0.14em] text-[#4a6080]">
                  CURRENT SAVED VALUES
                </p>
                <div className="flex flex-wrap gap-4">
                  {[
                    { label: 'RISK', value: `${settings.risk_percent}%`, color: '#00e5ff' },
                    { label: 'LEVERAGE', value: `${settings.leverage}×`, color: '#bf5af2' },
                    { label: 'MAX HOLD', value: `${settings.max_hold_hours}h`, color: '#ffd60a' },
                  ].map((item) => (
                    <div key={item.label} className="flex items-baseline gap-2">
                      <span className="font-mono text-[10px] text-[#4a6080]">{item.label}</span>
                      <span
                        className="font-mono text-sm font-bold tabular-nums"
                        style={{ color: item.color }}
                      >
                        {item.value}
                      </span>
                    </div>
                  ))}
                  <span className="font-mono text-[10px] text-[#2a3a54]">
                    Updated: {new Date(settings.updated_at).toLocaleString('ja-JP')}
                  </span>
                </div>
              </GlowCard>
            )}

            {/* Actions */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleSave}
                disabled={saving || !isDirty}
                className="flex-1 rounded border border-[#00e5ff]/30 bg-[#00e5ff]/10 px-6 py-3 font-mono text-[10px] font-bold tracking-[0.16em] text-[#00e5ff] transition-all hover:border-[#00e5ff]/60 hover:bg-[#00e5ff]/20 disabled:cursor-not-allowed disabled:opacity-30"
              >
                {saving ? 'SAVING...' : 'APPLY SETTINGS'}
              </button>
              <button
                onClick={handleReset}
                disabled={saving || !isDirty}
                className="rounded border border-[#1a2744] px-4 py-3 font-mono text-[10px] tracking-[0.12em] text-[#4a6080] transition-all hover:border-[#1e3a6e] hover:text-[#8ba3c4] disabled:cursor-not-allowed disabled:opacity-30"
              >
                RESET
              </button>
            </div>

            {/* Save result */}
            {saveResult === 'success' && (
              <p className="font-mono text-[10px] tracking-widest text-[#00ff88]">
                ✓ SETTINGS SAVED SUCCESSFULLY
              </p>
            )}
            {saveResult === 'error' && (
              <p className="font-mono text-[10px] tracking-widest text-[#ff3366]">
                ✗ SAVE FAILED — CHECK API CONNECTION
              </p>
            )}

            {/* Google auth placeholder note */}
            <GlowCard className="border-[#2a3a54] p-4 opacity-50">
              <p className="font-mono text-[10px] tracking-[0.12em] text-[#4a6080]">
                🔒 AUTHENTICATION — COMING SOON
              </p>
              <p className="mt-1 font-mono text-[10px] text-[#2a3a54]">
                Google account sign-in will be required to access this panel in a future update.
              </p>
            </GlowCard>
          </div>
        )}
      </div>

      {/* Global range slider style */}
      <style jsx global>{`
        input[type='range'] {
          cursor: pointer;
        }
        input[type='range']::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: var(--accent, #00e5ff);
          box-shadow: 0 0 8px var(--accent, #00e5ff);
          border: 2px solid #050810;
          cursor: pointer;
        }
        input[type='range']::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: var(--accent, #00e5ff);
          box-shadow: 0 0 8px var(--accent, #00e5ff);
          border: 2px solid #050810;
          cursor: pointer;
        }
        input[type='number']::-webkit-inner-spin-button,
        input[type='number']::-webkit-outer-spin-button {
          opacity: 0.3;
          filter: invert(1);
        }
      `}</style>
    </div>
  )
}
