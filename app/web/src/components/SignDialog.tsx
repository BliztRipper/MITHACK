import { useEffect, useRef, useState, type ReactNode } from 'react'
import { api, ApiError, type CaseRecord, type SignBody, type SignedLayers } from '../api'
import { LevelBadge } from './ui'

const REASONS = ['image misread', 'clinical findings disagree', 'poor image', 'other']

/** Missing items, listed above the Sign button; whitespace-only text counts as empty. */
export function missingItems(f: { decision: string; finding: string; reason: string; reasonText: string; crao: boolean | null }, emergency: boolean): string[] {
  const m: string[] = []
  if (!f.decision) m.push('Choose: confirm the AI result or override it')
  if (f.decision === 'override') {
    if (!f.finding.trim()) m.push('Enter your finding')
    if (!f.reason) m.push('Choose a reason for the override')
    if (f.reason === 'other' && !f.reasonText.trim()) m.push('Describe the reason ("other")')
  }
  if (emergency && f.crao === null) m.push('Answer: is this CRAO? (clinician assessment)')
  return m
}

/** Native modal <dialog>: focus is trapped by the browser and Esc cancels (design §3.13). */
export default function SignDialog({ c, layers, open, onClose, onSigned }: { c: CaseRecord; layers: SignedLayers; open: boolean; onClose: () => void; onSigned: () => void }): ReactNode {
  const ref = useRef<HTMLDialogElement>(null)
  const [decision, setDecision] = useState('')
  const [finding, setFinding] = useState('')
  const [reason, setReason] = useState('')
  const [reasonText, setReasonText] = useState('')
  const [crao, setCrao] = useState<boolean | null>(null)
  const [serverError, setServerError] = useState('')
  const [busy, setBusy] = useState(false)
  const emergency = c.mode === 'emergency'
  const a = c.analysis

  useEffect(() => {
    const d = ref.current
    if (open && d && !d.open) d.showModal()
    if (!open && d?.open) d.close()
  }, [open])

  const missing = missingItems({ decision, finding, reason, reasonText, crao }, emergency)
  const submit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    if (missing.length) return
    setBusy(true)
    setServerError('')
    const body: SignBody = { decision: decision as SignBody['decision'], layers } // the overlays on screen now become part of the record
    if (decision === 'override') Object.assign(body, { finding: finding.trim(), reason, ...(reason === 'other' ? { reason_text: reasonText.trim() } : {}) })
    if (emergency) body.crao = crao!
    try {
      await api.sign(c.report_id, body)
      onSigned()
    } catch (err) {
      const d = err instanceof ApiError ? err.detail : null
      setServerError(Array.isArray(d) ? d.map((x: { msg: string }) => x.msg).join('; ') : (err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  const radio = (name: string, value: string, label: string, checked: boolean, set: () => void, first = false): ReactNode => (
    <label className={`flex cursor-pointer items-center gap-3 rounded-md border px-3 py-2 ${checked ? 'border-accent bg-accent-tint' : 'border-rule-strong hover:bg-sunken'}`}>
      <input type="radio" className="check" name={name} value={value} checked={checked} onChange={set} autoFocus={first} />{label}
    </label>
  )

  return (
    <dialog ref={ref} onClose={onClose} aria-labelledby="sign-h" className="m-auto w-[560px] max-w-[calc(100vw-2rem)] max-h-[calc(100vh-2rem)] overflow-y-auto overscroll-contain rounded-lg border border-transparent bg-surface p-0 text-ink shadow-pop">
      <form onSubmit={submit} className="flex flex-col gap-4 p-6">
        <h2 id="sign-h" className="text-xl font-semibold">Sign result</h2>
        <div className="rounded-md bg-sunken p-3 text-sm">
          <p className="flex flex-wrap items-center gap-2">AI result: <LevelBadge level={c.level} />{a.crao?.band && <span className="font-mono">band {a.crao.band}</span>}</p>
          <p className="mt-1">{a.conclusion}</p>
          <p className="mt-1 font-mono">model {a.model_version}</p>
        </div>

        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 font-medium">Decision</legend>
          {radio('decision', 'confirm', 'Confirm AI result', decision === 'confirm', () => setDecision('confirm'), true)}
          {radio('decision', 'override', 'Override with my finding', decision === 'override', () => setDecision('override'))}
        </fieldset>

        {decision === 'override' && (
          <div className="flex flex-col gap-4">
            <label className="flex flex-col gap-1">Finding (required)
              <input className="input" value={finding} onChange={(e) => setFinding(e.target.value)} />
            </label>
            <fieldset className="flex flex-col gap-1">
              <legend className="mb-1">Reason (required)</legend>
              {REASONS.map((r) => (
                <label key={r} className="flex items-center gap-2"><input type="radio" className="check" name="reason" checked={reason === r} onChange={() => setReason(r)} />{r}</label>
              ))}
            </fieldset>
            <label className="flex flex-col gap-1">Details{reason === 'other' ? ' (required for "other")' : ''}
              <textarea className="input h-auto py-2" rows={2} value={reasonText} onChange={(e) => setReasonText(e.target.value)} />
            </label>
          </div>
        )}

        {emergency && (
          <fieldset className="flex flex-col gap-2">
            <legend className="font-medium">Clinician assessment: is this CRAO? (required)</legend>
            <p className="text-sm text-muted">Used to check model calibration.</p>
            <div className="grid grid-cols-2 gap-2">
              {radio('crao', 'yes', 'Yes, CRAO', crao === true, () => setCrao(true))}
              {radio('crao', 'no', 'No, not CRAO', crao === false, () => setCrao(false))}
            </div>
          </fieldset>
        )}

        {(missing.length > 0 || serverError) && (
          <ul aria-live="polite" className="list-disc pl-5 text-sm text-triage-stroke-fg">
            {missing.map((m) => <li key={m}>{m}</li>)}
            {serverError && <li>{serverError}</li>}
          </ul>
        )}
        <div className="flex justify-between gap-2">
          <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" disabled={busy || missing.length > 0}>{busy ? 'Signing…' : 'Sign as final'}</button>
        </div>
      </form>
    </dialog>
  )
}
