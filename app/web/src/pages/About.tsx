import { Fragment, type ReactNode } from 'react'
import { api } from '../api'
import { ErrorText, PageTitle, useLoad } from '../components/ui'
import modelCard from '../../../../docs/model-card.md?raw'

const UNITS: Record<string, string> = { hyperacute_h: 'h', acute_h: 'h', pce_band_edges: '%', ldl_statin_benefit: 'mg/dL',
  arcus_prompt_age: 'years', window: 'cases', calibration_min: 'cases', p_high: 'probability', p_low: 'probability', quality_min: 'score' }

const fmt = (v: unknown): string =>
  Array.isArray(v) ? v.join(' – ') : typeof v === 'object' && v !== null ? Object.entries(v).map(([k, x]) => `${k} ${fmt((x as { value: unknown }).value ?? x)}`).join('; ') : String(v)

function StatusChip({ status }: { status: string }): ReactNode {
  return status === 'placeholder'
    ? <span className="chip border border-dashed border-status-preliminary-border bg-status-preliminary-tint text-status-preliminary">placeholder, not clinically validated</span>
    : <span className="chip bg-status-final text-paper">{status}</span>
}

export default function About(): ReactNode {
  const { data, error } = useLoad(() => api.about(), [])
  if (error) return <ErrorText>{error}</ErrorText>
  if (!data) return <p>Loading…</p>
  const m = data.model
  return (
    <div className="flex max-w-5xl flex-col gap-10">
      <PageTitle>About</PageTitle>
      <section aria-labelledby="th-h">
        <h2 id="th-h" className="mb-2 text-xl font-semibold">Thresholds</h2>
        <p className="mb-2">CRAO bands in use: <span className="font-mono">{data.crao_thresholds.p_low} / {data.crao_thresholds.p_high}</span> (from {data.crao_thresholds.source}).</p>
        <table className="w-full text-left text-sm">
          <thead className="text-muted"><tr className="border-b border-rule-strong"><th className="py-1 pr-4 font-medium">Group</th><th className="pr-4 font-medium">Name</th>
            <th className="pr-4 font-medium">Value</th><th className="pr-4 font-medium">Unit</th><th className="font-medium">Status</th></tr></thead>
          <tbody>
            {Object.entries(data.config).flatMap(([group, items]) => Object.entries(items).map(([k, v]) => {
              const nested = !('status' in v) // e.g. pce_ranges: {age: {value, status}, …}
              return (
                <tr key={group + k} className="border-b border-rule align-top">
                  <td className="py-1 pr-4">{group}</td><td className="pr-4">{k.replaceAll('_', ' ')}</td>
                  <td className="pr-4 font-mono">{nested ? fmt(v) : fmt(v.value)}</td><td className="pr-4">{UNITS[k] ?? ''}</td>
                  <td><StatusChip status={nested ? String(Object.values(v as Record<string, { status: string }>)[0]?.status) : v.status} />
                    {v.source && <span className="ml-2 text-muted">{v.source}</span>}</td>
                </tr>
              )
            }))}
          </tbody>
        </table>
      </section>

      <section aria-labelledby="model-h">
        <h2 id="model-h" className="mb-2 text-xl font-semibold">Model</h2>
        {!m ? <p>No model loaded. Emergency cases are routed to ESCALATE.</p> : (
          <dl className="grid grid-cols-[12rem_minmax(0,1fr)] gap-x-4 gap-y-1">
            {Object.entries(m).map(([k, v]) => <Fragment key={k}><dt className="text-muted">{k.replaceAll('_', ' ')}</dt><dd className="font-mono">{fmt(v)}</dd></Fragment>)}
          </dl>
        )}
        <a href="#model-card" className="mt-2 inline-block text-accent underline">Model card</a>
      </section>

      <section aria-labelledby="lim-h">
        <h2 id="lim-h" className="mb-2 text-xl font-semibold">Limitations</h2>
        <ul className="list-disc pl-6">
          <li>The CRAO model was trained on established (not hyperacute) artery occlusions. An early CRAO can look normal on a fundus photo, so a normal-looking photo with a fitting story is escalated.</li>
          <li>The heatmap shows model attention, not lesions.</li>
          <li>PCE was not derived in Asian populations and may overestimate risk.</li>
          <li>Thresholds marked placeholder are not clinically validated; the artery-to-vein reference interval is a literature placeholder.</li>
          <li>Every result is preliminary until a clinician signs it. The tool does not diagnose.</li>
        </ul>
      </section>

      <section id="model-card" aria-labelledby="card-h">
        <h2 id="card-h" className="mb-2 text-xl font-semibold">Model card</h2>
        <pre className="card overflow-x-auto font-mono text-sm whitespace-pre-wrap">{modelCard}</pre>
      </section>
    </div>
  )
}
