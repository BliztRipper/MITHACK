import { useState, type ReactNode } from 'react'
import { Printer } from 'lucide-react'
import { api, mediaUrl, type CaseRecord, type OverlayKind } from '../api'
import { Amend, Decision, Disclosure, IncidentForm, PatientSummary } from '../components/ReportParts'
import ResultView from '../components/ResultView'
import SignDialog from '../components/SignDialog'
import { defaultLayers, fromSigned, layerCaption, toSigned, type Layers } from '../components/Stage'
import { ErrorText, useLoad, useSession } from '../components/ui'

/** Page margin boxes repeat on every printed page: preliminary warning, report id, page number. */
const pageStyle = (rid: string, preliminary: boolean): string => `@page {
  ${preliminary ? '@top-center { content: "PRELIMINARY · NOT A FINAL REPORT"; font: 600 10pt "IBM Plex Sans", sans-serif; }' : ''}
  @bottom-left { content: "Report ${rid}"; font: 9pt "IBM Plex Mono", monospace; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font: 9pt "IBM Plex Sans", sans-serif; }
}`

function CaseScreen({ c, reload }: { c: CaseRecord; reload: () => void }): ReactNode {
  const { storeDown } = useSession()
  const r = c.analysis
  const sign = c.reviews.find((x) => x.action === 'sign')
  const recorded = sign?.layers // the overlays visible when the case was signed, from the record
  const [layers, setLayers] = useState<Layers>(() => (recorded ? fromSigned(recorded) : defaultLayers(c.mode)))
  const [signing, setSigning] = useState(false)
  const fundus = c.media.find((m) => m.kind === 'fundus')
  const overlays = Object.fromEntries(c.media.filter((m) => m.kind !== 'fundus').map((m) => [m.kind, mediaUrl(m.id)])) as Partial<Record<OverlayKind, string>>
  const preliminary = c.status === 'preliminary'
  const caption = preliminary ? undefined : recorded ? layerCaption('Layers shown at signing', recorded) : 'Layers shown at signing: not recorded.'
  const signBlock = storeDown ? 'record store unavailable' : !c.can_sign ? 'only the case owner or the reviewer of an escalated case can sign' : ''

  return (
    <>
      <style>{pageStyle(c.report_id, preliminary)}</style>
      <ResultView r={r} fundus={fundus ? mediaUrl(fundus.id) : ''} overlays={overlays} patient={c.patient} status={c.status}
        signer={sign?.user} issued={c.issued} layers={layers} setLayers={setLayers} caption={caption}>
        <div className="flex flex-wrap items-start gap-2 print:hidden">
          {preliminary && (
            <div>
              <button className="btn-primary" disabled={Boolean(signBlock)} onClick={() => setSigning(true)}>Sign result</button>
              {signBlock && <p className="mt-1 text-sm text-muted">Cannot sign: {signBlock}.</p>}
            </div>
          )}
          <button className="btn-secondary" onClick={() => print()}><Printer size={20} aria-hidden />Print report</button>
        </div>
        <Decision reviews={c.reviews} />
        <Disclosure preliminary={preliminary} />
        {!preliminary && <PatientSummary rid={c.report_id} />}
        {!preliminary && <Amend c={c} onDone={reload} disabled={storeDown} />}
        <IncidentForm rid={c.report_id} disabled={storeDown} />
      </ResultView>
      {preliminary && !signBlock && (
        <SignDialog c={c} layers={toSigned(layers, overlays, Boolean(r.segmentation?.disc_found))} open={signing} onClose={() => setSigning(false)} onSigned={() => {
          setSigning(false)
          reload()
        }} />
      )}
    </>
  )
}

export default function Case({ id }: { id: string }): ReactNode {
  const { data, error, reload } = useLoad(() => api.case(id), [id])
  if (error) return <ErrorText>{error}</ErrorText>
  if (!data) return <p>Loading…</p>
  if (!data.analysis?.quality) return <p>This case has no AI record (seeded history): {data.conclusion}</p>
  return <CaseScreen key={data.status} c={data} reload={reload} />
}
