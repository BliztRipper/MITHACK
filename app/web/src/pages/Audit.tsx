import { useState, type ReactNode } from 'react'
import { api } from '../api'
import { ErrorText, fmtTime, PageTitle, useLoad } from '../components/ui'

const ACTIONS: Record<string, string> = { C: 'create', R: 'read', U: 'update', D: 'delete', E: 'export' }
const OUTCOMES: Record<string, string> = { '0': 'success', '4': 'refused', '8': 'error' }

/** Read-only audit trail (admin). */
export default function Audit(): ReactNode {
  const [days, setDays] = useState(1)
  const { data, error } = useLoad(() => api.audit(days), [days])
  return (
    <>
      <PageTitle>Audit log</PageTitle>
      <label className="mb-4 flex max-w-xs flex-col gap-1">Period
        <select className="input" value={days} onChange={(e) => setDays(Number(e.target.value))}>
          {[1, 7, 30].map((d) => <option key={d} value={d}>last {d} day{d > 1 ? 's' : ''}</option>)}
        </select>
      </label>
      <ErrorText>{error}</ErrorText>
      {data && data.length === 0 && <p>No audit events in this period.</p>}
      {data && data.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-muted"><tr className="border-b border-rule-strong"><th className="py-1 pr-4 font-medium">Time</th><th className="pr-4 font-medium">User</th>
              <th className="pr-4 font-medium">Role</th><th className="pr-4 font-medium">Action</th><th className="pr-4 font-medium">Outcome</th><th className="font-medium">Resource</th></tr></thead>
            <tbody>
              {data.map((a) => (
                <tr key={a.id} className="border-b border-rule">
                  <td className="py-1 pr-4 tabular-nums">{fmtTime(a.time)}</td><td className="pr-4">{a.user}</td><td className="pr-4">{a.role}</td>
                  <td className="pr-4">{ACTIONS[a.action] ?? a.action}</td><td className="pr-4">{OUTCOMES[a.outcome] ?? a.outcome}</td>
                  <td className="font-mono">{a.resource}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
