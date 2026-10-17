import { createContext, useContext, useEffect, useState, type AnchorHTMLAttributes, type ReactNode } from 'react'
import { CalendarClock, Camera, CircleAlert, FileCheck2, FilePen, OctagonAlert, TriangleAlert, UserRoundSearch, type LucideIcon } from 'lucide-react'
import type { Level, User } from '../api'

// ---- routing: history API, no router dependency ----
export function navigate(to: string): void {
  history.pushState(null, '', to)
  dispatchEvent(new PopStateEvent('popstate'))
}

/** Current pathname + search; re-renders on navigation. */
export function usePath(): string {
  const [p, setP] = useState(location.pathname + location.search)
  useEffect(() => {
    const f = (): void => setP(location.pathname + location.search)
    addEventListener('popstate', f)
    return () => removeEventListener('popstate', f)
  }, [])
  return p
}

export function Link({ href, ...rest }: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }): ReactNode {
  return (
    <a href={href} {...rest} onClick={(e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return
      e.preventDefault()
      navigate(href)
    }} />
  )
}

// ---- session: the signed-in user and record-store health ----
export interface SessionValue { user: User; storeDown: boolean }
export const Session = createContext<SessionValue | null>(null)
export const useSession = (): SessionValue => useContext(Session)!

// ---- vocabulary (design §3.1) ----
export const LEVELS: Record<Level, { label: string; icon: LucideIcon; badge: string; card: string }> = {
  STROKE_PATHWAY: { label: 'STROKE PATHWAY', icon: OctagonAlert,
    badge: 'bg-triage-stroke-tint text-triage-stroke-fg border-2 border-triage-stroke', card: 'bg-triage-stroke text-paper' },
  URGENT: { label: 'URGENT', icon: TriangleAlert,
    badge: 'bg-triage-urgent-tint text-triage-urgent-fg', card: 'bg-triage-urgent-tint text-triage-urgent-fg border-2 border-triage-urgent' },
  ESCALATE: { label: 'ESCALATE: specialist review', icon: UserRoundSearch,
    badge: 'bg-triage-escalate-tint text-triage-escalate-fg', card: 'bg-surface text-ink border-2 border-triage-escalate' },
  RETAKE: { label: 'RETAKE PHOTO', icon: Camera,
    badge: 'bg-triage-retake-tint text-triage-retake border border-dashed border-triage-retake', card: 'bg-surface text-ink border-2 border-dashed border-triage-retake' },
  ROUTINE: { label: 'ROUTINE', icon: CalendarClock,
    badge: 'bg-triage-routine-tint text-triage-routine', card: 'bg-surface text-ink border border-rule-strong' },
}

/** Row badge for a triage level, or a neutral badge for Screening codes (pce-<band>, bypass, not-valid). */
export function LevelBadge({ level }: { level: string | null }): ReactNode {
  const l = level && LEVELS[level as Level]
  if (!l) return <span className="chip border border-rule-strong text-ink">{level?.replace('pce-', 'PCE ') ?? '—'}</span>
  const Icon = l.icon
  return <span className={`chip py-0.5 font-medium ${l.badge}`}><Icon size={16} aria-hidden />{l.label}</span>
}

export function StatusBadge({ status, signer }: { status: string; signer?: string }): ReactNode {
  if (status === 'preliminary')
    return (
      <span className="chip py-1 text-sm border-[1.5px] border-dashed border-status-preliminary-border bg-status-preliminary-tint text-status-preliminary">
        <FilePen size={16} aria-hidden />PRELIMINARY · AI-assisted, not a diagnosis
      </span>
    )
  return (
    <span className="chip py-1 text-sm bg-status-final text-paper print:border print:border-black">
      <FileCheck2 size={16} aria-hidden />FINAL{signer ? ` · signed by ${signer}` : ''}{status === 'amended' ? ' · amended' : ''}
    </span>
  )
}

export const Placeholder = (): ReactNode => <span className="chip-placeholder">placeholder</span>

export function ErrorText({ id, children }: { id?: string; children: ReactNode }): ReactNode {
  if (!children) return null
  return <p id={id} className="mt-1 flex items-center gap-1 text-sm text-triage-stroke-fg"><CircleAlert size={16} aria-hidden />{children}</p>
}

export const fmtDate = (s: string | null | undefined): string =>
  s ? new Date(s).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
export const fmtTime = (s: string | null | undefined): string =>
  s ? new Date(s).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—'

export function ageOf(birth: string | null): number | null {
  if (!birth) return null
  const b = new Date(birth), n = new Date()
  return n.getFullYear() - b.getFullYear() - (n < new Date(n.getFullYear(), b.getMonth(), b.getDate()) ? 1 : 0)
}

export function PageTitle({ children }: { children: ReactNode }): ReactNode {
  return <h1 className="mb-6 text-xl font-semibold">{children}</h1>
}
