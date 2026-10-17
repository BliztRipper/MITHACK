import { useState, type ReactNode } from 'react'
import { api, type Consent } from '../api'
import { ageOf, ErrorText, fmtDate, Link, PageTitle, StatusBadge, useLoad, useSession } from '../components/ui'

export const consentWords = (c: Consent): string => `care: ${c.care ? 'yes' : 'no'} · model use: ${c.model_improvement ? 'yes' : 'no'}`

const LABELS: Record<string, string> = { sbp: 'Systolic BP', dbp: 'Diastolic BP', tc: 'Total cholesterol', hdl: 'HDL', ldl: 'LDL',
  smoking: 'Smoking', arcus_senilis: 'Arcus senilis' }

export default function Patient({ id }: { id: string }): ReactNode {
  const { storeDown } = useSession()
  const { data, error, reload } = useLoad(() => api.patient(id), [id])
  const [confirming, setConfirming] = useState(false)
  const [wError, setWError] = useState('')

  if (error) return <ErrorText>{error}</ErrorText>
  if (!data) return <p>Loading…</p>
  const { patient: p, consent, latest, cases } = data
  const anyConsent = consent.care || consent.model_improvement

  const withdraw = async (): Promise<void> => {
    setWError('')
    try {
      await api.withdraw(id)
      setConfirming(false)
      reload()
    } catch (e) {
      setWError((e as Error).message)
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <PageTitle>{p.name}</PageTitle>
          <p className="-mt-4 text-muted">HN <span className="font-mono text-ink">{p.hn ?? '—'}</span> · {p.gender ?? '—'} · born {fmtDate(p.birth_date)} ({ageOf(p.birth_date) ?? '—'} y)</p>
        </div>
        <Link href={`/new/${id}`} className="btn-primary">New case for this patient</Link>
      </div>

      <section aria-labelledby="consent-h" className="card max-w-3xl">
        <h2 id="consent-h" className="mb-2 font-semibold">Consent</h2>
        <p>{consentWords(consent)}</p>
        {anyConsent && !confirming && (
          <button className="btn-secondary mt-4" disabled={storeDown} onClick={() => setConfirming(true)}>Withdraw consent</button>
        )}
        {storeDown && anyConsent && <p className="mt-1 text-sm text-muted">Withdrawal unavailable: record store unavailable.</p>}
        {confirming && (
          <div className="mt-4 flex flex-col gap-3 rounded-md border border-triage-urgent bg-triage-urgent-tint p-4">
            <p>Withdrawing erases this patient's retinal images (keys destroyed). Signed report text is kept. This cannot be undone.</p>
            <div className="flex gap-2">
              <button className="btn-primary" onClick={withdraw}>Confirm withdrawal</button>
              <button className="btn-secondary" onClick={() => setConfirming(false)}>Cancel</button>
            </div>
            <ErrorText>{wError}</ErrorText>
          </div>
        )}
      </section>

      <section aria-labelledby="cases-h">
        <h2 id="cases-h" className="mb-2 font-semibold">Prior cases</h2>
        {cases.length === 0 ? <p className="text-muted">No prior cases.</p> : (
          <table className="w-full max-w-5xl text-left">
            <thead className="text-sm text-muted"><tr className="border-b border-rule-strong">
              <th className="py-2 pr-4 font-medium">Date</th><th className="pr-4 font-medium">Mode</th><th className="pr-4 font-medium">Result</th><th className="font-medium">Status</th></tr></thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.report_id} className="h-12 border-b border-rule hover:bg-sunken row-hover">
                  <td className="pr-4 tabular-nums"><Link href={`/cases/${c.report_id}`} className="text-accent hover:underline">{fmtDate(c.date)}</Link></td>
                  <td className="pr-4 capitalize">{c.mode}</td>
                  <td className="pr-4">{c.result ?? '—'}</td>
                  <td><StatusBadge status={c.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {Object.keys(latest).length > 0 && (
        <section aria-labelledby="latest-h">
          <h2 id="latest-h" className="mb-2 font-semibold">Recent values on record</h2>
          <table className="text-left text-sm">
            <tbody>
              {Object.entries(latest).map(([k, v]) => (
                <tr key={k} className="border-b border-rule"><th className="py-1 pr-6 font-medium">{LABELS[k] ?? k}</th>
                  <td className="pr-6 font-mono">{String(v!.value)}</td><td className="text-muted">{fmtDate(v!.date)}</td></tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}
