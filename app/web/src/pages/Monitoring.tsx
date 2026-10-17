import { useState, type ReactNode } from 'react'
import { Flag, TriangleAlert } from 'lucide-react'
import { api, type FlagView, type Level, type Rate, type VersionMetrics } from '../api'
import { ErrorText, fmtTime, LEVELS, Link, PageTitle, Placeholder, useLoad, useSession } from '../components/ui'

const pct = (v: number | null): string => (v === null ? '—' : `${Math.round(v * 100)} %`)

function Tile({ title, children }: { title: string; children: ReactNode }): ReactNode {
  return <section className="card flex flex-col gap-2"><h2 className="font-medium">{title}</h2>{children}</section>
}

/** One row per model version: value, n, and a thin bar with the configured limit tick. */
function RateTile({ title, metrics, pick, limit }: { title: string; metrics: VersionMetrics[]; pick: (m: VersionMetrics) => Rate; limit?: number }): ReactNode {
  return (
    <Tile title={title}>
      {metrics.map((m) => {
        const r = pick(m)
        return (
          <div key={m.version}>
            <p><span className="font-mono text-2xl">{pct(r.value)}</span> <span className="ml-2 font-mono text-sm text-muted">n = {r.n} · {m.version}</span></p>
            {limit !== undefined && (
              <div className="relative mt-1 h-1.5 bg-sunken" aria-hidden>
                <div className="h-full bg-rule-strong" style={{ width: `${(r.value ?? 0) * 100}%` }} />
                <div className="absolute -top-1 h-3.5 w-0.5 bg-ink" style={{ left: `${limit * 100}%` }} />
              </div>
            )}
          </div>
        )
      })}
      {limit !== undefined && <p className="text-sm text-muted">limit {pct(limit)} <Placeholder /></p>}
    </Tile>
  )
}

function Counts({ title, metrics, pick }: { title: string; metrics: VersionMetrics[]; pick: (m: VersionMetrics) => Record<string, number> }): ReactNode {
  return (
    <Tile title={title}>
      {metrics.map((m) => {
        const c = pick(m), total = Object.values(c).reduce((a, b) => a + b, 0)
        return (
          <div key={m.version} className="text-sm">
            <p className="font-mono text-muted">{m.version} · n = {total}</p>
            {total === 0 && <p>None.</p>}
            {Object.entries(c).map(([k, v]) => (
              <div key={k} className="grid grid-cols-[10rem_minmax(0,1fr)_3rem] items-center gap-2">
                <span>{LEVELS[k as Level]?.label ?? k.replace('_', ' ')}</span>
                <div className="h-2 bg-sunken"><div className="h-full bg-rule-strong" style={{ width: `${(v / total) * 100}%` }} /></div>
                <span className="font-mono tabular-nums">{v}</span>
              </div>
            ))}
          </div>
        )
      })}
    </Tile>
  )
}

function FlagRow({ f, kind, canClose, onDone }: { f: FlagView; kind: 'alert' | 'incident'; canClose: boolean; onDone: () => void }): ReactNode {
  const [open, setOpen] = useState(false)
  const [note, setNote] = useState('')
  const [error, setError] = useState('')
  const Icon = kind === 'alert' ? TriangleAlert : Flag
  const submit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    try {
      await (kind === 'alert' ? api.acknowledge(f.id, note.trim()) : api.closeIncident(f.id, note.trim()))
      onDone()
    } catch (err) {
      setError((err as Error).message)
    }
  }
  return (
    <li className="flex flex-col gap-2 rounded-md bg-system-warn-tint p-3">
      <div className="flex flex-wrap items-start gap-2">
        <Icon size={20} className="mt-0.5 shrink-0" aria-hidden />
        <div className="flex-1">
          <p>{f.text}</p>
          <p className="font-mono text-sm text-muted">{f.metric ?? 'incident'} · opened {fmtTime(f.opened)}
            {f.case && <> · <Link href={`/cases/${f.case.split('/')[1]}`} className="text-accent underline">{f.case}</Link></>}</p>
        </div>
        {canClose && !open && <button className="btn-secondary" onClick={() => setOpen(true)}>{kind === 'alert' ? 'Acknowledge' : 'Close'}</button>}
      </div>
      {open && (
        <form onSubmit={submit} className="flex flex-wrap items-end gap-2">
          <label className="flex flex-1 flex-col gap-1">Note (required)<input className="input" value={note} onChange={(e) => setNote(e.target.value)} /></label>
          <button className="btn-primary" disabled={!note.trim()}>{kind === 'alert' ? 'Acknowledge' : 'Close incident'}</button>
          <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancel</button>
          <ErrorText>{error}</ErrorText>
        </form>
      )}
    </li>
  )
}

export default function Monitoring(): ReactNode {
  const { user } = useSession()
  const [days, setDays] = useState(30)
  const { data, error, reload } = useLoad(() => api.monitoring(days), [days])
  const about = useLoad(() => api.about(), [])
  const lim = (k: string): number | undefined => about.data?.config.monitoring[k]?.value as number | undefined
  const admin = user.role === 'admin'

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <PageTitle>Monitoring</PageTitle>
        <div className="flex flex-wrap items-end gap-4">
          <label className="flex flex-col gap-1">Period
            <select className="input" value={days} onChange={(e) => setDays(Number(e.target.value))}>
              {[7, 30, 90].map((d) => <option key={d} value={d}>last {d} days</option>)}
            </select>
          </label>
          {data && <p className="pb-2">Current model <span className="font-mono">{data.current_version}</span></p>}
          {admin && <a className="btn-secondary" href="/api/monitoring/export" download>Export reviewed cases (de-identified)</a>}
        </div>
      </div>
      <ErrorText>{error}</ErrorText>
      {data && (
        <>
          <section aria-labelledby="cal-h">
            <h2 id="cal-h" className="mb-2 text-xl font-semibold">Calibration on signed Emergency cases</h2>
            {data.calibration.status === 'insufficient data' ? (
              <div className="rounded-lg border-2 border-dotted border-rule-strong bg-sunken p-4">
                <p className="text-lg font-medium">Insufficient data ({data.calibration.n} of {data.calibration.needed})</p>
                <p className="text-sm">Calibration is shown once {data.calibration.needed} signed Emergency cases with a probability band exist for the current model version.</p>
              </div>
            ) : (
              <table className="text-left"><thead className="text-sm text-muted"><tr className="border-b border-rule-strong">
                <th className="py-1 pr-6 font-medium">Band</th><th className="pr-6 font-medium">n</th><th className="pr-6 font-medium">Mean predicted p</th><th className="font-medium">Observed CRAO rate</th></tr></thead>
                <tbody>{Object.entries(data.calibration.bands).map(([b, v]) => (
                  <tr key={b} className="border-b border-rule"><td className="py-1 pr-6">{b}</td><td className="pr-6 font-mono">{v.n}</td>
                    <td className="pr-6 font-mono">{v.mean_p ?? '—'}</td><td className="font-mono">{pct(v.observed_crao_rate)}</td></tr>))}</tbody>
              </table>
            )}
          </section>

          <section aria-labelledby="alerts-h">
            <h2 id="alerts-h" className="mb-2 text-xl font-semibold">Drift alerts</h2>
            {data.alerts.length === 0 ? <p className="text-muted">No open alerts (alerts need a full window of {lim('window') ?? 50} cases).</p> : (
              <ul className="flex flex-col gap-2">{data.alerts.map((f) => <FlagRow key={f.id} f={f} kind="alert" canClose={admin} onDone={reload} />)}</ul>
            )}
          </section>

          <section aria-labelledby="inc-h">
            <h2 id="inc-h" className="mb-2 text-xl font-semibold">Open incidents</h2>
            {data.incidents.length === 0 ? <p className="text-muted">No open incidents.</p> : (
              <ul className="flex flex-col gap-2">{data.incidents.map((f) => <FlagRow key={f.id} f={f} kind="incident" canClose={admin} onDone={reload} />)}</ul>
            )}
          </section>

          <section aria-labelledby="met-h">
            <h2 id="met-h" className="mb-2 text-xl font-semibold">Metrics, last {data.period_days} days</h2>
            {data.metrics.length === 0 ? <p>No cases in this period.</p> : (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <Counts title="Cases by mode" metrics={data.metrics} pick={(m) => m.by_mode} />
                <RateTile title="Quality rejection rate" metrics={data.metrics} pick={(m) => m.quality_rejection_rate} limit={lim('quality_reject_max')} />
                <RateTile title="Uncertain-band rate" metrics={data.metrics} pick={(m) => m.uncertain_rate} limit={lim('uncertain_max')} />
                <RateTile title="Agreement rate" metrics={data.metrics} pick={(m) => m.agreement_rate} limit={lim('agreement_max')} />
                <Counts title="Override reasons" metrics={data.metrics} pick={(m) => m.override_reasons} />
                <Counts title="Triage levels (Emergency)" metrics={data.metrics} pick={(m) => m.triage_levels} />
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}
