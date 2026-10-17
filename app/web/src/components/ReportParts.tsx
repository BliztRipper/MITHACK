import { useState, type ReactNode } from 'react'
import { api, type CaseRecord, type Review } from '../api'
import { ErrorText, fmtTime, useLoad } from './ui'

/** Who signed, when, confirm/override, reason and the CRAO answer; amendments follow. */
export function Decision({ reviews }: { reviews: Review[] }): ReactNode {
  return (
    <section aria-labelledby="decision-h" className="card print-plain">
      <h2 id="decision-h" className="mb-2 font-semibold">Clinician decision</h2>
      {reviews.length === 0 && <p>Not signed yet. This result is preliminary.</p>}
      <dl className="flex flex-col gap-3">
        {reviews.map((r) => (
          <div key={r.at} className="grid grid-cols-[8rem_minmax(0,1fr)] gap-x-3 text-sm">
            <dt className="text-muted">{r.action === 'sign' ? 'Signed' : 'Amended'}</dt><dd>{r.user} · {fmtTime(r.at)}</dd>
            {r.decision && <><dt className="text-muted">Decision</dt><dd>{r.decision === 'confirm' ? 'Confirmed AI result' : 'Overrode AI result'}</dd></>}
            {r.finding && <><dt className="text-muted">Finding</dt><dd className="font-medium">{r.finding}</dd></>}
            {r.reason && <><dt className="text-muted">Reason</dt><dd>{r.reason}</dd></>}
            {r.reason_text && <><dt className="text-muted">Details</dt><dd>{r.reason_text}</dd></>}
            {r.crao != null && <><dt className="text-muted">CRAO (clinical)</dt><dd>{r.crao ? 'Yes, CRAO' : 'No, not CRAO'}</dd></>}
            {r.ai_conclusion && r.decision === 'override' && <><dt className="text-muted">AI output</dt><dd>{r.ai_conclusion}</dd></>}
          </div>
        ))}
      </dl>
    </section>
  )
}

export function Disclosure(): ReactNode {
  return (
    <section aria-labelledby="disc-h" className="text-sm">
      <h2 id="disc-h" className="font-semibold">AI-assisted, not a diagnosis</h2>
      <p>The image analysis, probability and suggested actions were produced by software and checked by the clinician named above. Thresholds marked placeholder are not clinically validated.</p>
    </section>
  )
}

/** Fixed-template Thai/English summary, available after signing (design §3.17). */
export function PatientSummary({ rid }: { rid: string }): ReactNode {
  const [lang, setLang] = useState<'th' | 'en'>('th')
  const { data, error } = useLoad(() => api.summary(rid, lang), [rid, lang])
  return (
    <section aria-labelledby="sum-h" className="card print-plain">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h2 id="sum-h" className="font-semibold">Patient summary</h2>
        <div role="radiogroup" aria-label="Summary language" className="flex overflow-hidden rounded-md border border-rule-strong print:hidden">
          {(['th', 'en'] as const).map((l) => (
            <button key={l} role="radio" aria-checked={lang === l} onClick={() => setLang(l)}
              className={`px-3 py-1 ${lang === l ? 'bg-accent text-paper' : 'bg-surface'} ${l === 'th' ? 'font-thai' : ''}`}>
              {l === 'th' ? 'ภาษาไทย' : 'English'}
            </button>
          ))}
        </div>
      </div>
      <ErrorText>{error}</ErrorText>
      {data && (
        <div lang={data.lang} className={data.lang === 'th' ? 'font-thai text-[12pt] leading-[1.7]' : ''}>
          <p>{data.text[0]}</p>
          <p className="font-bold">{data.text[1]}</p>
        </div>
      )}
    </section>
  )
}

export function Amend({ c, onDone, disabled }: { c: CaseRecord; onDone: () => void; disabled: boolean }): ReactNode {
  const [open, setOpen] = useState(false)
  const [finding, setFinding] = useState('')
  const [why, setWhy] = useState('')
  const [error, setError] = useState('')
  const history = useLoad(() => (c.status === 'amended' ? api.history(c.report_id) : Promise.resolve([])), [c.status, c.report_id])
  const submit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    try {
      await api.amend(c.report_id, { finding: finding.trim(), reason_text: why.trim() })
      setOpen(false)
      onDone()
    } catch (err) {
      setError((err as Error).message)
    }
  }
  return (
    <div className="flex flex-col gap-3 print:hidden">
      {history.data && history.data.length > 0 && (
        <details className="text-sm"><summary className="cursor-pointer text-accent">History ({history.data.length} versions)</summary>
          <ol className="mt-1 list-decimal pl-5">{history.data.map((h) => <li key={h.version}>{h.status} · {fmtTime(h.updated)} · {h.conclusion}</li>)}</ol>
        </details>
      )}
      {!open ? <button className="btn-secondary self-start" disabled={disabled} onClick={() => setOpen(true)}>Amend report</button> : (
        <form onSubmit={submit} className="card flex flex-col gap-3">
          <label className="flex flex-col gap-1">Amended finding<input className="input" value={finding} onChange={(e) => setFinding(e.target.value)} /></label>
          <label className="flex flex-col gap-1">Reason for amendment<input className="input" value={why} onChange={(e) => setWhy(e.target.value)} /></label>
          <ErrorText>{error}</ErrorText>
          <div className="flex gap-2">
            <button className="btn-primary" disabled={!finding.trim() || !why.trim()}>Save amendment</button>
            <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancel</button>
          </div>
        </form>
      )}
    </div>
  )
}

/** Any clinician can flag a suspected AI safety incident; it stays on the dashboard until an admin closes it. */
export function IncidentForm({ rid, disabled }: { rid: string; disabled: boolean }): ReactNode {
  const [open, setOpen] = useState(false)
  const [text, setText] = useState('')
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')
  const submit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    try {
      await api.incident(rid, text.trim())
      setDone(true)
      setOpen(false)
    } catch (err) {
      setError((err as Error).message)
    }
  }
  if (done) return <p className="text-sm print:hidden">Incident flagged for the monitoring dashboard.</p>
  return !open ? <button className="btn-secondary self-start print:hidden" disabled={disabled} onClick={() => setOpen(true)}>Flag AI safety incident</button> : (
    <form onSubmit={submit} className="card flex flex-col gap-3 print:hidden">
      <label className="flex flex-col gap-1">What happened? (required)
        <textarea className="input h-auto py-2" rows={2} value={text} onChange={(e) => setText(e.target.value)} />
      </label>
      <ErrorText>{error}</ErrorText>
      <div className="flex gap-2">
        <button className="btn-primary" disabled={!text.trim()}>Flag incident</button>
        <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancel</button>
      </div>
    </form>
  )
}
