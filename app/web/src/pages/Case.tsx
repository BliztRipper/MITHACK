import { useState, type ReactNode } from 'react'
import { api, mediaUrl, type CaseRecord, type OverlayKind } from '../api'
import ResultView from '../components/ResultView'
import { defaultLayers, type Layers } from '../components/Stage'
import { ErrorText, useLoad } from '../components/ui'

// shortcut: the layers shown at signing are kept in this browser's localStorage, not in the record; move to the API if reports are printed elsewhere.
export const layersKey = (rid: string): string => `layers:${rid}`

function CaseScreen({ c }: { c: CaseRecord }): ReactNode {
  const r = c.analysis
  const [layers, setLayers] = useState<Layers>(() => {
    const saved = c.status !== 'preliminary' && localStorage.getItem(layersKey(c.report_id))
    return saved ? JSON.parse(saved) : defaultLayers(c.mode)
  })
  const fundus = c.media.find((m) => m.kind === 'fundus')
  const overlays = Object.fromEntries(c.media.filter((m) => m.kind !== 'fundus').map((m) => [m.kind, mediaUrl(m.id)])) as Partial<Record<OverlayKind, string>>
  const sign = c.reviews.find((x) => x.action === 'sign')

  return (
    <ResultView r={r} fundus={fundus ? mediaUrl(fundus.id) : ''} overlays={overlays} patient={c.patient} status={c.status}
      signer={sign?.user} issued={c.issued} layers={layers} setLayers={setLayers} />
  )
}

export default function Case({ id }: { id: string }): ReactNode {
  const { data, error } = useLoad(() => api.case(id), [id])
  if (error) return <ErrorText>{error}</ErrorText>
  if (!data) return <p>Loading…</p>
  if (!data.analysis?.quality) return <p>This case has no AI record (seeded history): {data.conclusion}</p>
  return <CaseScreen c={data} />
}
