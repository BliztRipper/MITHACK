import { useEffect, useState, type CSSProperties, type ReactNode } from 'react'
import { Columns2, Info } from 'lucide-react'
import { useSession } from './ui'
import type { CaseResult, OverlayKind, SignedLayers } from '../api'

export interface Layers { vessels: 'off' | 'all' | 'av'; disc: boolean; heatmap: boolean; opacity: number }
export const defaultLayers = (mode: string): Layers =>
  mode === 'emergency' ? { vessels: 'off', disc: true, heatmap: true, opacity: 70 } : { vessels: 'av', disc: true, heatmap: false, opacity: 70 }

const NAMES: Record<OverlayKind, string> = { vessel: 'all vessels', artery_vein: 'artery (yellow) / vein (blue)', disc: 'optic disc ring', heatmap: 'model attention heatmap' }

/** The layers actually visible, as stored with a signature. */
export function toSigned(l: Layers, overlays: Partial<Record<OverlayKind, string>>, discFound: boolean): SignedLayers {
  const on: Record<OverlayKind, boolean> = { vessel: l.vessels === 'all', artery_vein: l.vessels === 'av', disc: l.disc && discFound, heatmap: l.heatmap }
  return { visible: (Object.keys(on) as OverlayKind[]).filter((k) => on[k] && (k === 'disc' || Boolean(overlays[k]))), opacity: l.opacity }
}

export const fromSigned = (s: SignedLayers): Layers => ({
  vessels: s.visible.includes('artery_vein') ? 'av' : s.visible.includes('vessel') ? 'all' : 'off',
  disc: s.visible.includes('disc'), heatmap: s.visible.includes('heatmap'), opacity: s.opacity,
})

export const layerCaption = (prefix: string, s: SignedLayers): string =>
  `${prefix}: ${s.visible.map((k) => NAMES[k]).join(', ') || 'none'}, opacity ${s.opacity} %.`

const mask = (src: string, colour: string, opacity: number): CSSProperties =>
  ({ background: colour, maskImage: `url("${src}")`, WebkitMaskImage: `url("${src}")`, opacity: opacity / 100 })

interface Props {
  fundus: string
  overlays: Partial<Record<OverlayKind, string>> // URL (data: or /api/media/…) per layer
  seg: CaseResult['segmentation']
  layers: Layers
  setLayers: (l: Layers) => void
  caption?: string // print caption; defaults to the layers visible now
}

function Picture({ fundus, overlays, seg, layers, bare, label }: Omit<Props, 'setLayers'> & { bare?: boolean; label: string }): ReactNode {
  const [size, setSize] = useState<[number, number] | null>(null)
  const o = layers.opacity
  return (
    <figure className="m-0">
      <div className="relative mx-auto aspect-square max-h-[78vh] print:max-h-none">
        <img src={fundus} alt={label} className="absolute inset-0 h-full w-full object-contain"
          onLoad={(e) => setSize([e.currentTarget.naturalWidth, e.currentTarget.naturalHeight])} />
        {!bare && layers.vessels === 'all' && overlays.vessel &&
          <div className="mask absolute inset-0" style={mask(overlays.vessel, 'var(--color-overlay-vessel)', o)} aria-hidden />}
        {!bare && layers.vessels === 'av' && overlays.artery_vein &&
          <img src={overlays.artery_vein} alt="" className="absolute inset-0 h-full w-full object-contain" style={{ opacity: o / 100, filter: 'var(--shadow-halo)' }} />}
        {!bare && layers.heatmap && overlays.heatmap &&
          <div className="mask absolute inset-0" style={mask(overlays.heatmap, 'var(--color-overlay-heatmap)', o)} aria-hidden />}
        {!bare && layers.disc && seg?.disc_centre && seg.disc_diameter && size && (
          <svg viewBox={`0 0 ${size[0]} ${size[1]}`} className="absolute inset-0 h-full w-full" style={{ opacity: o / 100, filter: 'var(--shadow-halo)' }} aria-hidden>
            <circle cx={seg.disc_centre[0]} cy={seg.disc_centre[1]} r={seg.disc_diameter / 2} fill="none" stroke="var(--color-overlay-disc)"
              strokeWidth={2} strokeDasharray="6 4" vectorEffect="non-scaling-stroke" />
            <text x={seg.disc_centre[0]} y={seg.disc_centre[1] - seg.disc_diameter / 2 - 8} textAnchor="middle" fill="var(--color-overlay-disc)"
              fontSize={Math.max(14, size[0] / 40)}>Disc</text>
          </svg>
        )}
      </div>
      <figcaption className="mt-2 text-center text-sm text-stage-ink print:text-black">{label}</figcaption>
    </figure>
  )
}

function Switch({ label, swatch, pattern, on, disabled, why, onChange }: { label: string; why?: string; swatch: string; pattern: string; on: boolean; disabled?: boolean; onChange: (v: boolean) => void }): ReactNode {
  return (
    <button role="switch" aria-checked={on} disabled={disabled} aria-describedby={disabled ? why : undefined} onClick={() => onChange(!on)}
      className="flex items-center gap-2 rounded-md border border-stage-muted px-3 py-1.5 text-left hover:bg-stage-ink/10 disabled:opacity-60 disabled:hover:bg-transparent">
      <span className="size-3 shrink-0 rounded-sm" style={{ background: swatch }} aria-hidden />
      <span>{label} <span className="text-stage-muted">({pattern})</span></span>
      <span className="ml-2 font-mono text-sm">{on ? 'On' : 'Off'}</span>
    </button>
  )
}

export default function Stage({ fundus, overlays, seg, layers, setLayers, caption }: Props): ReactNode {
  const [compare, setCompare] = useState(false)
  useEffect(() => {
    if (!compare) return
    const f = (e: KeyboardEvent): void => { if (e.key === 'Escape') setCompare(false) }
    addEventListener('keydown', f)
    return () => removeEventListener('keydown', f)
  }, [compare])
  const set = (patch: Partial<Layers>): void => setLayers({ ...layers, ...patch })
  const vesselOpts: [Layers['vessels'], string, string, string][] = [
    ['off', 'Off', 'transparent', ''], ['all', 'All vessels', 'var(--color-overlay-vessel)', 'filaments'],
    ['av', 'Artery / vein', 'linear-gradient(90deg, var(--color-overlay-artery) 50%, var(--color-overlay-vein) 50%)', 'two colours'],
  ]
  const discFound = Boolean(seg?.disc_found)
  const vesselOff = (v: Layers['vessels']): boolean => (v === 'all' ? !overlays.vessel : v === 'av' ? !overlays.artery_vein : false)
  const { storeDown } = useSession()

  return (
    <div className="stage bg-stage p-4 text-stage-ink">
      <div className={compare ? 'grid grid-cols-2 gap-4 print:block' : ''}>
        {compare && <div className="print:hidden"><Picture fundus={fundus} overlays={overlays} seg={seg} layers={layers} bare label="Original (unaltered)" /></div>}
        <Picture fundus={fundus} overlays={overlays} seg={seg} layers={layers} label={compare ? 'With layers' : 'Fundus photo with selected layers'} />
      </div>
      {layers.heatmap && overlays.heatmap && (
        <p className="mt-2 flex items-center justify-center gap-1 text-sm"><Info size={16} aria-hidden />Heatmap shows model attention, not lesions.</p>
      )}

      <div className="mt-4 flex flex-col gap-4 border-t border-stage-muted/40 pt-4 print:hidden">
        <fieldset>
          <legend className="mb-1 text-sm text-stage-muted">Vessels</legend>
          <div className="flex flex-wrap gap-2">
            {vesselOpts.map(([v, label, swatch, pattern]) => (
              <label key={v} className={`flex cursor-pointer items-center gap-2 rounded-md border px-3 py-1.5 ${layers.vessels === v ? 'border-focus-dark bg-stage-ink/10' : 'border-stage-muted hover:bg-stage-ink/10'}`}>
                <input type="radio" name="vessels" className="size-4" checked={layers.vessels === v} onChange={() => set({ vessels: v })}
                  disabled={vesselOff(v)} aria-describedby={vesselOff(v) ? 'vessel-why' : undefined} />
                {v !== 'off' && <span className="size-3 rounded-sm" style={{ background: swatch }} aria-hidden />}
                {label}{pattern && <span className="text-stage-muted">({pattern})</span>}
              </label>
            ))}
          </div>
          {(vesselOff('all') || vesselOff('av')) && (
            <p id="vessel-why" className="mt-1 text-sm">Vessel layer not available{storeDown ? ': record store unavailable' : ' for this case'}.</p>
          )}
        </fieldset>
        <div className="flex flex-wrap gap-2">
          <Switch label="Optic disc" swatch="var(--color-overlay-disc)" pattern="dashed ring" on={layers.disc && discFound} disabled={!discFound} why="disc-why" onChange={(v) => set({ disc: v })} />
          <Switch label="Model attention (heatmap)" swatch="var(--color-overlay-heatmap)" pattern="glow" on={layers.heatmap && Boolean(overlays.heatmap)} disabled={!overlays.heatmap} why="heat-why" onChange={(v) => set({ heatmap: v })} />
          <button className="flex items-center gap-2 rounded-md border border-stage-muted px-3 py-1.5 hover:bg-stage-ink/10" aria-pressed={compare} onClick={() => setCompare(!compare)}>
            <Columns2 size={20} aria-hidden />{compare ? 'Exit compare' : 'Compare side by side'}
          </button>
        </div>
        {!discFound && seg && <p id="disc-why" className="text-sm">Optic disc not located; region-based explanation omitted.</p>}
        {!overlays.heatmap && <p id="heat-why" className="text-sm text-stage-muted">Heatmap not available for this case.</p>}
        {!seg && <p className="text-sm">Segmentation not available for this image: no vessel or disc layers.</p>}
        <label className="flex items-center gap-3">
          <span>Overlay opacity</span>
          <input type="range" min={0} max={100} step={5} value={layers.opacity} onChange={(e) => set({ opacity: Number(e.target.value) })} className="w-48" />
          <span className="font-mono text-sm tabular-nums">{layers.opacity} %</span>
        </label>
      </div>
      <p className="hidden text-sm text-stage-ink print:block print:text-black">{caption ?? layerCaption('Layers shown', toSigned(layers, overlays, discFound))}</p>
    </div>
  )
}
