import type { ReactNode } from 'react'
import { DatabaseZap } from 'lucide-react'
import type { CaseResult, OverlayKind } from '../api'
import { Gauge, TriageCard } from './Emergency'
import RiskPanel from './RiskPanel'
import Stage, { type Layers } from './Stage'
import { fmtTime, StatusBadge } from './ui'

// region code -> the words the explanation template uses (rules/templates/en.json)
const REGION: Record<string, string> = { macula: 'macula', optic_disc: 'optic disc', arcades: 'vascular arcades', periphery: 'peripheral retina' }

function Explanation({ r }: { r: CaseResult }): ReactNode {
  const region = r.explanation.region && REGION[r.explanation.region]
  const bold = (s: string): ReactNode => {
    if (!region || !s.includes(region)) return s
    const [a, ...b] = s.split(region)
    return <>{a}<strong className="font-semibold">{region}</strong>{b.join(region)}</>
  }
  const noRegion = r.mode === 'emergency' && r.crao?.probability != null && !r.explanation.region
  return (
    <section aria-labelledby="expl-h">
      <h2 id="expl-h" className="mb-1 font-semibold">What the model looked at</h2>
      {r.explanation.sentences.length === 0 && <p>No explanation: the image was not analysed.</p>}
      <p className="max-w-[65ch]">{r.explanation.sentences.map((s, i) => <span key={i}>{bold(s)} </span>)}</p>
      {noRegion && <p className="mt-1">The optic disc was not located, so no region is named. Confirm on the image.</p>}
    </section>
  )
}

interface Props {
  r: CaseResult
  fundus: string
  overlays: Partial<Record<OverlayKind, string>>
  patient: { name: string; hn: string | null }
  status: string
  signer?: string
  issued?: string | null
  layers: Layers
  setLayers: (l: Layers) => void
  children?: ReactNode // clinician decision, disclosure, patient summary
}

/** The result screen (design §3.8). DOM order is the print order; CSS order gives the screen layout. */
export default function ResultView({ r, fundus, overlays, patient, status, signer, issued, layers, setLayers, children }: Props): ReactNode {
  const q = r.quality
  return (
    <div className="flex flex-col gap-6">
      <header className="sticky top-0 z-10 -mx-4 flex flex-wrap items-center justify-between gap-4 border-b border-rule bg-paper px-4 py-3 print:static print:mx-0 print:px-0">
        <div>
          <h1 className="text-xl font-semibold">{patient.name} <span className="font-mono text-base font-normal">{patient.hn}</span></h1>
          <p className="text-muted print:text-black">
            <span className="font-semibold uppercase">{r.mode}</span> · {fmtTime(issued)} · <span className="font-mono">
              quality {q.score.toFixed(2)}, {q.accept ? 'passed' : 'failed'}</span> · model <span className="font-mono">{r.model_version}</span>
          </p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <StatusBadge status={status} signer={signer} />
          {status !== 'preliminary' && <span className="text-sm">{r.label}</span>}
        </div>
        {r.save_error && (
          <p role="alert" className="flex w-full items-center gap-2 border-b-2 border-triage-urgent bg-system-warn-tint px-3 py-2 font-medium">
            <DatabaseZap size={20} aria-hidden />{r.save_error}. This result cannot be signed.
          </p>
        )}
      </header>

      <div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_420px] print:block">
        <div className="order-2 xl:order-1 print:mb-4">
          <Stage fundus={fundus} overlays={overlays} seg={r.segmentation} layers={layers} setLayers={setLayers} />
        </div>
        <div className="order-1 flex flex-col gap-6 xl:order-2 print:gap-4">
          {r.mode === 'emergency' && r.crao && <div className="order-2 print:order-none"><Gauge crao={r.crao} /></div>}
          <div className="order-1 print:order-none">
            {r.mode === 'emergency' && r.triage && <TriageCard triage={r.triage} />}
            {r.mode === 'screening' && r.risk && <RiskPanel r={r} />}
          </div>
          <div className="order-3 print:order-none"><Explanation r={r} /></div>
          <div className="order-4 flex flex-col gap-6 print:order-none">{children}</div>
        </div>
      </div>
    </div>
  )
}
