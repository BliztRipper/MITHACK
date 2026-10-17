import type { ReactNode } from 'react'
import { Info, Pill } from 'lucide-react'
import type { Crao, Triage } from '../api'
import { LEVELS, Placeholder } from './ui'

const BAND_TEXT = { unlikely: 'text-band-unlikely', uncertain: 'text-band-uncertain', likely: 'text-band-likely' }

/** Calibrated probability on a bar split at the (placeholder) thresholds (design §3.9). */
export function Gauge({ crao }: { crao: Crao }): ReactNode {
  const m = crao.model
  if (crao.probability === null || !crao.band)
    return (
      <section aria-labelledby="gauge-h" className="rounded-lg bg-sunken p-4 print:border print:border-black">
        <h2 id="gauge-h" className="mb-1 font-semibold">CRAO probability</h2>
        <p>{crao.status === 'no model loaded'
          ? 'No model loaded. Probability not available. Case routed to ESCALATE.'
          : `Probability not available: ${crao.status}.`}</p>
      </section>
    )
  const p = crao.probability, lo = crao.p_low * 100, hi = crao.p_high * 100
  return (
    <section aria-labelledby="gauge-h" className="gauge flex flex-col gap-2">
      <h2 id="gauge-h" className="font-semibold">CRAO probability</h2>
      <div className="flex items-baseline gap-4">
        <span className="font-mono text-3xl">p = {p.toFixed(2)}</span>
        <span className={`text-2xl font-semibold ${BAND_TEXT[crao.band]}`}>{crao.band}</span>
      </div>
      {crao.band === 'uncertain' && <p>Not a positive or negative finding. Specialist review recommended.</p>}
      <div className="relative mt-4" role="img" aria-label={`Probability ${p.toFixed(2)} in the ${crao.band} band; thresholds ${crao.p_low} and ${crao.p_high}`}>
        <div className="absolute -top-3 h-0 w-0 -translate-x-1/2 border-x-[6px] border-t-[8px] border-x-transparent border-t-ink" style={{ left: `${p * 100}%` }} />
        <div className="absolute -top-1 z-10 h-6 w-0.5 -translate-x-1/2 bg-ink" style={{ left: `${p * 100}%` }} />
        <div className="flex h-4 w-full overflow-hidden border border-rule-strong">
          <div className="bg-sunken" style={{ width: `${lo}%` }} />
          <div className="hatch" style={{ width: `${hi - lo}%` }} />
          <div className="bg-band-likely" style={{ width: `${100 - hi}%` }} />
        </div>
        <div className="flex text-sm">
          <span style={{ width: `${lo}%` }}>unlikely</span>
          <span style={{ width: `${hi - lo}%` }}>uncertain</span>
          <span style={{ width: `${100 - hi}%` }}>likely</span>
        </div>
      </div>
      <p className="font-mono text-sm">thresholds {crao.p_low.toFixed(2)} · {crao.p_high.toFixed(2)} <Placeholder /></p>
      <p className="font-mono text-sm text-muted">{m ? `${m.model} ${m.version} · calibrated ${m.calibration_date ?? 'uncalibrated'}` : 'model unknown'}</p>
    </section>
  )
}

const PLACEHOLDER_RULE = /[≥≤<>]|uncertain band/ // a reason that compares against a configured threshold

/** The decision: level, numbered actions, verbatim rule reasons and limitations (design §3.10). */
export function TriageCard({ triage }: { triage: Triage }): ReactNode {
  const l = LEVELS[triage.level]
  const Icon = l.icon
  const solid = triage.level === 'STROKE_PATHWAY'
  return (
    <section aria-labelledby="triage-h" className={`lvl-${triage.level} print-plain flex flex-col gap-4 rounded-lg p-4 ${l.card}`}>
      <div>
        <h2 id="triage-h" className="flex items-center gap-2 text-2xl font-semibold uppercase tracking-wide"><Icon size={24} aria-hidden />{l.label}</h2>
        <p className={`font-mono text-xs ${solid ? 'text-paper' : 'text-muted'}`}>{triage.level}</p>
      </div>
      <ol className="list-decimal pl-6 text-lg">
        {triage.actions.map((a, i) => (
          <li key={a} className={i === 0 ? 'font-semibold' : ''}>
            {i === 0 && a.includes('arteritis') && <Pill size={20} className="mr-1 inline align-text-bottom" aria-hidden />}{a}
          </li>
        ))}
      </ol>
      <div>
        <h3 className="mb-1 font-semibold">Why this level</h3>
        <ul className="font-mono text-sm">
          {triage.reasons.map((r) => <li key={r}>{r}{PLACEHOLDER_RULE.test(r) && ' (placeholder)'}</li>)}
        </ul>
      </div>
      <p className={`flex gap-2 rounded-md p-3 text-sm ${solid ? 'border border-paper/70' : 'bg-sunken text-ink'}`}>
        <Info size={16} className="mt-0.5 shrink-0" aria-hidden />
        Trained on established (not hyperacute) artery occlusions. An early CRAO can look normal on a fundus photo.
      </p>
    </section>
  )
}
