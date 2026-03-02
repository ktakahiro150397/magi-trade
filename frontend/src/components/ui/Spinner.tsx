import { clsx } from 'clsx'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeMap = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-[3px]',
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <div
      className={clsx(
        'animate-spin rounded-full border-solid border-[#00e5ff] border-t-transparent',
        sizeMap[size],
        className
      )}
    />
  )
}

export function LoadingState({ label = 'LOADING...' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <Spinner size="lg" />
      <p className="font-mono text-xs tracking-widest text-[#4a6080]">{label}</p>
    </div>
  )
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16">
      <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[#ff3366]/30 bg-[#ff3366]/10">
        <span className="font-mono text-lg text-[#ff3366]">!</span>
      </div>
      <p className="font-mono text-xs tracking-widest text-[#ff3366]">ERROR</p>
      <p className="max-w-xs text-center text-sm text-[#8ba3c4]">{message}</p>
    </div>
  )
}
