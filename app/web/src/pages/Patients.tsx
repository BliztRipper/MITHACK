import { useState, type ReactNode } from 'react'
import { api, fieldErrors, type PatientSummary } from '../api'
import { ageOf, ErrorText, fmtDate, Link, navigate, PageTitle, useLoad } from '../components/ui'

/** Search by name or HN (POST body, never the URL); each row links to hrefFor(id). */
export function PatientSearch({ hrefFor }: { hrefFor: (id: string) => string }): ReactNode {
  const [q, setQ] = useState('')
  const [rows, setRows] = useState<PatientSummary[] | null>(null)
  const [searched, setSearched] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [pick, setPick] = useState('')
  const all = useLoad(() => api.patients(), []) // demo mode: pick from every synthetic patient instead of typing

  if (!all.data && !all.error) return null // until we know which form to show, so typing is never swapped away
  if (all.data?.length) return (
    // navigate on submit, not on change: arrow keys on a closed select fire change in Chrome/Firefox
    <form onSubmit={(e) => { e.preventDefault(); if (pick) navigate(hrefFor(pick)) }} className="mb-6 flex max-w-xl items-end gap-2">
      <label className="flex flex-1 flex-col gap-1">Choose a patient (HN)
        <select className="input" value={pick} onChange={(e) => setPick(e.target.value)}>
          <option value="" disabled>Select HN…</option>
          {all.data.map((p) => <option key={p.id} value={p.id}>{p.hn ?? '—'} · {p.name || '(no name)'}</option>)}
        </select>
      </label>
      <button className="btn-primary" disabled={!pick}>Open</button>
    </form>
  )

  const submit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    if (!q.trim()) return
    setBusy(true)
    setError('')
    try {
      setRows(await api.search(q.trim()))
      setSearched(q.trim())
    } catch (err) {
      setError(fieldErrors(err)._ ?? 'Search failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <form onSubmit={submit} role="search" className="mb-6 flex max-w-xl items-end gap-2">
        <label className="flex flex-1 flex-col gap-1">Search name or HN
          <input className="input" value={q} onChange={(e) => setQ(e.target.value)} />
        </label>
        <button className="btn-primary" disabled={busy || !q.trim()}>{busy ? 'Searching…' : 'Search'}</button>
      </form>
      <ErrorText>{error}</ErrorText>
      {rows && rows.length === 0 && <p>No patient matches '{searched}'.</p>}
      {rows && rows.length > 0 && (
        <table className="w-full max-w-4xl text-left">
          <thead className="text-sm text-muted">
            <tr className="border-b border-rule-strong"><th className="py-2 pr-4 font-medium">HN</th><th className="pr-4 font-medium">Name</th>
              <th className="pr-4 font-medium">Sex</th><th className="font-medium">Date of birth / age</th></tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id} className="h-12 cursor-pointer border-b border-rule hover:bg-sunken row-hover" onClick={(e) => { if (!(e.target as Element).closest('a')) navigate(hrefFor(p.id)) }}>
                <td className="pr-4 font-mono">{p.hn ?? '—'}</td>
                <td className="pr-4"><Link href={hrefFor(p.id)} className="text-accent underline-offset-2 hover:underline">{p.name || '(no name)'}</Link></td>
                <td className="pr-4">{p.gender ?? '—'}</td>
                <td className="tabular-nums">{fmtDate(p.birth_date)} · {ageOf(p.birth_date) ?? '—'} y</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default function Patients(): ReactNode {
  return <><PageTitle>Patients</PageTitle><PatientSearch hrefFor={(id) => `/patients/${id}`} /></>
}
