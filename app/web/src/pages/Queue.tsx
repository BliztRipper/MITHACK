import type { ReactNode } from 'react'
import { Clock } from 'lucide-react'
import { api } from '../api'
import { ErrorText, LevelBadge, Link, PageTitle, StatusBadge, useLoad, useSession } from '../components/ui'

/** Awaiting signature, in the API's order (Emergency first, then longest waiting); never re-sorted here. */
export default function Queue(): ReactNode {
  const { user } = useSession()
  const { data, error } = useLoad(() => api.queue(), [])
  return (
    <>
      <PageTitle>Review queue</PageTitle>
      <ErrorText>{error}</ErrorText>
      {data && data.length === 0 && <p>No cases are waiting for signature.</p>}
      {data && data.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="text-sm text-muted"><tr className="border-b border-rule-strong">
              <th className="py-2 pr-4 font-medium">Level</th><th className="pr-4 font-medium">Mode</th><th className="pr-4 font-medium">Patient</th>
              <th className="pr-4 font-medium">Waiting</th><th className="pr-4 font-medium">Conclusion</th><th className="font-medium">Status</th></tr></thead>
            <tbody>
              {data.map((c) => {
                const em = c.mode === 'emergency'
                const late = em && (c.waiting_minutes ?? 0) > 30
                return (
                  <tr key={c.report_id} className="h-12 border-b border-rule hover:bg-sunken">
                    <td className="pr-4"><LevelBadge level={c.level} />
                      {user.role === 'reviewer' && c.level === 'ESCALATE' && <span className="ml-2 text-sm text-triage-escalate-fg">escalated to you</span>}</td>
                    <td className={`pr-4 ${em ? 'font-semibold' : ''}`}>{em ? 'EMERGENCY' : 'Screening'}</td>
                    <td className="pr-4"><Link href={`/cases/${c.report_id}`} className="text-accent hover:underline">{c.patient?.name || `Case ${c.report_id}`}</Link>
                      <span className="ml-2 font-mono text-sm text-muted">{c.patient?.hn ?? '—'}</span></td>
                    <td className={`whitespace-nowrap pr-4 font-mono tabular-nums ${late ? 'font-semibold text-triage-urgent-fg' : ''}`}>
                      {late && <Clock size={16} className="mr-1 inline align-text-bottom" aria-label="waiting over 30 minutes" />}
                      {c.waiting_minutes === null ? '—' : `${Math.round(c.waiting_minutes)} min`}</td>
                    <td className="max-w-[28ch] truncate pr-4" title={c.conclusion ?? ''}>{c.conclusion}</td>
                    <td><StatusBadge status={c.status} /></td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
