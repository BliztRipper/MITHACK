import type { ReactNode } from 'react'
import { Info } from 'lucide-react'
import type { CaseResult, Measure } from '../api'
import { Placeholder } from './ui'

const PCE_BANDS = [['low', '<5 %'], ['borderline', '5–<7.5'], ['intermediate', '7.5–<20'], ['high', '≥20']]
const RISK_BG = ['bg-risk-1 text-ink', 'bg-risk-2 text-ink', 'bg-risk-3 text-ink font-semibold', 'bg-risk-4 text-paper']

function OrdinalBar({ bands, current }: { bands: string[][]; current: string | null }): ReactNode {
  return (
    <div className="gauge grid grid-cols-4 gap-0.5 text-sm" role="img" aria-label={`band: ${current ?? 'none'}`}>
      {bands.map(([name, range], i) => (
        <div key={name} className={`relative px-1 py-1 text-center ${RISK_BG[i]} ${name === current ? 'outline-2 outline-ink -outline-offset-2' : ''}`}>
          {name === current && <span className="absolute -top-3 left-1/2 h-0 w-0 -translate-x-1/2 border-x-[6px] border-t-[8px] border-x-transparent border-t-ink" aria-hidden />}
          {range}
        </div>
      ))}
    </div>
  )
}

const Note = ({ children }: { children: ReactNode }): ReactNode =>
  <p className="flex gap-2 text-sm"><Info size={16} className="mt-0.5 shrink-0" aria-hidden />{children}</p>

function MeasureRow({ name, m }: { name: string; m: Measure }): ReactNode {
  return (
    <tr className="border-b border-rule">
      <th className="py-1 pr-3 text-left font-medium">{name}</th>
      <td className="whitespace-nowrap pr-3 text-right font-mono tabular-nums">{m.value === null ? '—' : m.value.toFixed(m.unit === 'px' ? 1 : 2)}{m.unit ? ` ${m.unit}` : ''}</td>
      <td className="pr-3 text-right font-mono tabular-nums">{m.reference ? <>{m.reference[0]}–{m.reference[1]} <Placeholder /></> : '—'}</td>
      <td>{m.flag === 'not_assessed' ? `not assessed (${m.reason})` : m.flag ?? '—'}</td>
    </tr>
  )
}

/** Screening result: PCE with caveat, bypass, enhancers, measurements, suggestion (design §3.11). */
export default function RiskPanel({ r }: { r: CaseResult }): ReactNode {
  const risk = r.risk!
  const { pce } = risk
  return (
    <section aria-labelledby="risk-h" className="flex flex-col gap-6">
      <h2 id="risk-h" className="sr-only">10-year cardiovascular risk</h2>
      {risk.bypass ? (
        <p className="rounded-lg border-2 border-ink p-4 text-lg font-medium">{risk.bypass}</p>
      ) : (
        <>
          <div className="flex flex-col gap-2">
            <h3 className="font-semibold">{pce.label}</h3>
            {pce.not_valid ? <p>{pce.not_valid}</p> : pce.risk !== null && (
              <>
                <p><span className="font-mono text-xl">{pce.risk.toFixed(1)} %</span>{' '}10-year ASCVD risk · <span className="font-semibold">{pce.band}</span></p>
                <OrdinalBar bands={PCE_BANDS} current={pce.band} />
              </>
            )}
            {pce.notes.map((n) => <p key={n} className="text-sm text-muted">{n}</p>)}
          </div>
        </>
      )}

      <div>
        <h3 className="mb-1 font-semibold">Risk enhancers</h3>
        {risk.enhancers.retinal.length + risk.enhancers.clinical.length === 0 && <p className="text-sm">None recorded.</p>}
        <ul className="flex flex-col gap-1">
          {risk.enhancers.retinal.map((e) => <li key={e}><span className="chip mr-2 border border-rule-strong">retinal</span>{e}</li>)}
          {risk.enhancers.clinical.map((e) => <li key={e}><span className="chip mr-2 border border-rule-strong">clinical</span>{e}</li>)}
        </ul>
        {risk.enhancers.not_assessed && <p className="mt-1 text-sm">{risk.enhancers.not_assessed}</p>}
        {risk.enhancers.note && <p className="mt-1 text-sm">{risk.enhancers.note}</p>}
        <p className="mt-1 text-sm text-muted">Enhancers do not change the calculated risk.</p>
      </div>

      {r.measurements && (
        <div>
          <h3 className="mb-1 font-semibold">Retinal vessel measurements</h3>
          <table className="w-full text-sm">
            <thead className="text-muted"><tr className="border-b border-rule-strong text-left">
              <th className="py-1 pr-3 font-medium">Measure</th><th className="whitespace-nowrap pr-3 text-right font-medium">Value</th><th className="pr-3 text-right font-medium">Reference</th><th className="font-medium">Flag</th></tr></thead>
            <tbody>
              <MeasureRow name="AVR" m={r.measurements.avr} />
              <MeasureRow name="CRAE" m={r.measurements.crae} />
              <MeasureRow name="CRVE" m={r.measurements.crve} />
            </tbody>
          </table>
        </div>
      )}

      {pce.suggestion && !risk.bypass && (
        <div className="rounded-md border border-rule bg-surface p-3">
          <h3 className="text-sm font-medium text-muted">{pce.suggestion_label}</h3>
          <p>{pce.suggestion}</p>
        </div>
      )}
      {risk.htn_stage1 && <Note>{risk.htn_stage1}</Note>}
      {risk.arcus && <Note>{risk.arcus}</Note>}
    </section>
  )
}
