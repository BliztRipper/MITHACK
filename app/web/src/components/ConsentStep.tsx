import { useEffect, useState, type ReactNode } from 'react'
import { api, ApiError, type Consent } from '../api'
import { ErrorText } from './ui'

/** Consent gate (design §3.5): a wizard step that fails closed when consent cannot be verified. */
export default function ConsentStep({ patientId, onReady }: { patientId: string; onReady: (ok: boolean) => void }): ReactNode {
  const [consent, setConsent] = useState<Consent | null>(null)
  const [blocked, setBlocked] = useState('')
  const [editing, setEditing] = useState(false)
  const [care, setCare] = useState(false)
  const [model, setModel] = useState(false)
  const [years, setYears] = useState('10')
  const [explained, setExplained] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.consent(patientId).then((c) => { setConsent(c); onReady(c.care) }).catch((e) => {
      setBlocked(e instanceof ApiError && e.status === 503
        ? 'Cannot verify consent while the record store is down. Analysis is blocked.'
        : `Cannot verify consent: ${(e as Error).message}. Analysis is blocked.`)
      onReady(false)
    })
  }, [patientId, onReady])

  if (blocked) return <div role="alert" className="max-w-2xl rounded-lg border-2 border-triage-urgent bg-system-warn-tint p-4 font-medium">{blocked}</div>
  if (!consent) return <p>Checking consent…</p>

  if (consent.care && !editing)
    return (
      <p>Consent on file: care {consent.care ? 'yes' : 'no'}, model use {consent.model_improvement ? 'yes' : 'no'}.{' '}
        <button className="text-accent underline" onClick={() => { setEditing(true); setModel(consent.model_improvement) }}>Edit</button></p>
    )

  const n = Number(years)
  const missing = [!care && 'care use', !explained && 'right to withdraw', !(Number.isInteger(n) && n >= 1) && 'retention of 1 year or more'].filter(Boolean)
  const submit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const c = await api.recordConsent(patientId, { care: true, model_improvement: model, retention_years: n, right_to_withdraw_explained: true })
      setConsent(c)
      setEditing(false)
      onReady(c.care)
    } catch (err) {
      setError(err instanceof ApiError && err.status === 503 ? 'Record store unavailable: consent was not recorded.' : (err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className="card flex max-w-2xl flex-col gap-4">
      <h2 className="text-xl font-semibold">Consent required before analysis</h2>
      <p>Retinal photos are biometric health data under Thai PDPA section 26, so explicit consent must be recorded before any image is processed.</p>
      <label className="flex items-center gap-2"><input type="checkbox" className="check" checked={care} onChange={(e) => setCare(e.target.checked)} />Care use (required)</label>
      <div>
        <label className="flex items-center gap-2"><input type="checkbox" className="check" checked={model} onChange={(e) => setModel(e.target.checked)} />Use for model improvement (optional)</label>
        <p className="ml-7 text-sm text-muted">Refusing changes nothing about the patient's care.</p>
      </div>
      <label className="flex max-w-xs flex-col gap-1">Retention (years)
        <input className="input" type="number" min={1} step={1} value={years} onChange={(e) => setYears(e.target.value)} />
      </label>
      <label className="flex items-center gap-2"><input type="checkbox" className="check" checked={explained} onChange={(e) => setExplained(e.target.checked)} />Right to withdraw explained to patient (required)</label>
      <div>
        <button className="btn-primary" disabled={busy || missing.length > 0}>{busy ? 'Recording…' : 'Record consent and continue'}</button>
        {missing.length > 0 && <p className="mt-1 text-sm text-muted">Tick: {missing.join(', ')}</p>}
        <ErrorText>{error}</ErrorText>
      </div>
    </form>
  )
}
