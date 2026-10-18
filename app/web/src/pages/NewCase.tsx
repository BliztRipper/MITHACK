import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { Camera, Check, LoaderCircle, TriangleAlert } from 'lucide-react'
import { api, ApiError, demoImageUrl, demoMessage, fieldErrors, type CaseResult, type Mode, type PatientDetail } from '../api'
import ConsentStep from '../components/ConsentStep'
import InputsForm, { initialValues, toInputs, validate, type Values } from '../components/InputsForm'
import ResultView from '../components/ResultView'
import { defaultLayers, type Layers } from '../components/Stage'
import { ErrorText, Link, navigate, PageTitle, useLoad } from '../components/ui'
import { PatientSearch } from './Patients'

const STEPS = ['Mode', 'Consent', 'Inputs', 'Photo', 'Result']
const sentence = (s: string): string => s.charAt(0).toUpperCase() + s.slice(1)

function StepList({ step, go }: { step: number; go: (i: number) => void }): ReactNode {
  return (
    <ol className="mb-8 flex flex-wrap gap-6 border-b border-rule print:hidden">
      {STEPS.map((s, i) => (
        <li key={s} aria-current={i === step ? 'step' : undefined}
          className={`-mb-px pb-2 ${i === step ? 'border-b-2 border-accent font-semibold text-ink' : 'text-muted'}`}>
          {i < step ? (
            <button className="flex items-center gap-1 hover:underline" onClick={() => go(i)}><Check size={16} aria-hidden />{i + 1}. {s}</button>
          ) : `${i + 1}. ${s}`}
        </li>
      ))}
    </ol>
  )
}

function ModeStep({ mode, setMode }: { mode: Mode | null; setMode: (m: Mode) => void }): ReactNode {
  const opt = (m: Mode, title: string, line: string, icon?: ReactNode): ReactNode => (
    <label className={`flex cursor-pointer flex-col gap-2 rounded-lg border-2 p-4 ${mode === m ? 'border-accent bg-accent-tint' : 'border-rule-strong bg-surface hover:bg-sunken'}`}>
      <span className="flex items-center gap-2 text-lg font-semibold">
        <input type="radio" name="mode" className="check" checked={mode === m} onChange={() => setMode(m)} />{icon}{title}
        {mode === m && <Check size={20} className="ml-auto text-accent" aria-hidden />}
      </span>
      <span className="text-muted">{line}</span>
    </label>
  )
  return (
    <fieldset className="grid max-w-4xl gap-4 md:grid-cols-2">
      <legend className="sr-only">Mode</legend>
      {opt('screening', 'Screening: 10-year CVD risk', 'Retinal vessel measurements from the photo; add lab values for the 10-year risk.')}
      {opt('emergency', 'Emergency: sudden vision loss', 'Use for sudden, painless loss of vision in one eye', <TriangleAlert size={20} className="text-triage-urgent" aria-hidden />)}
    </fieldset>
  )
}

function RetakeCard({ r, preview, onRetake }: { r: CaseResult; preview: string; onRetake: () => void }): ReactNode {
  return (
    <div className="grid max-w-5xl gap-8 md:grid-cols-[minmax(0,320px)_minmax(0,1fr)]">
      <div className="stage bg-stage p-4"><img src={preview} alt="Fundus photo that failed the quality check" className="aspect-square w-full object-contain" /></div>
      <section className="lvl-RETAKE flex flex-col gap-4 rounded-lg border-2 border-dashed border-triage-retake bg-surface p-4" aria-labelledby="retake-h">
        <h2 id="retake-h" className="flex items-center gap-2 text-2xl font-semibold uppercase tracking-wide"><Camera size={24} aria-hidden />Retake photo</h2>
        <ul className="list-disc pl-6">{r.quality.reasons.map((x) => <li key={x}>{sentence(x)}</li>)}</ul>
        <p className="font-mono text-sm">quality {r.quality.score.toFixed(2)}, below threshold (placeholder)</p>
        {r.mode === 'emergency' && <p className="text-lg font-medium">If a gradable photo cannot be taken within minutes, refer urgently. Do not delay.</p>}
        <div className="flex flex-wrap gap-2">
          <button className="btn-primary" onClick={onRetake}><Camera size={20} aria-hidden />Retake photo</button>
          {r.report_id && <Link href={`/cases/${r.report_id}`} className="btn-secondary">Open saved case</Link>}
        </div>
      </section>
    </div>
  )
}

function Wizard({ patient }: { patient: PatientDetail }): ReactNode {
  const pid = patient.patient.id
  const [step, setStep] = useState(0)
  const [mode, setModeState] = useState<Mode | null>(null)
  const [consentOk, setConsentOk] = useState(false)
  const [values, setValues] = useState<Values>({})
  const [dates, setDates] = useState<Record<string, string>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<CaseResult | null>(null)
  const [layers, setLayers] = useState<Layers>(defaultLayers('screening'))
  const demoImages = useLoad(() => api.demoImages(), []).data ?? []
  const onReady = useCallback((ok: boolean) => setConsentOk(ok), [])

  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview) }, [preview])
  const setMode = (m: Mode): void => {
    setModeState(m)
    const init = initialValues(m, patient)
    setValues(init.values)
    setDates(init.dates)
    setErrors({})
  }
  const pick = (f: File | null): void => {
    setFile(f)
    setPreview(f ? URL.createObjectURL(f) : '')
    setResult(null)
    setErrors({})
  }
  const pickCached = async (name: string): Promise<void> => {
    const r = await fetch(demoImageUrl(name))
    if (!r.ok) return setErrors({ _: 'Demo photos are not available right now. Try again in a minute.' })
    pick(new File([await r.blob()], name, { type: name.endsWith('.jpg') ? 'image/jpeg' : 'image/png' }))
  }
  const next = (): void => {
    if (step === 2) {
      const e = validate(mode!, values)
      setErrors(e)
      if (Object.keys(e).length) return
    }
    setStep(step + 1)
  }
  const analyse = async (): Promise<void> => {
    if (!file || !mode) return
    setBusy(true)
    setErrors({})
    const f = new FormData()
    f.set('patient_id', pid)
    f.set('mode', mode)
    f.set('inputs', JSON.stringify(toInputs(mode, values)))
    f.set('image', file)
    try {
      const r = await api.createCase(f)
      setResult(r)
      if (r.quality.accept && r.report_id) return navigate(`/cases/${r.report_id}`)
      if (r.quality.accept) { setLayers(defaultLayers(mode)); setStep(4) }
    } catch (e) {
      // 403 no consent / 409 consent withdrawn: say why here; going back to the consent step could loop
      if (e instanceof ApiError && (e.status === 403 || e.status === 409)) { setConsentOk(false); setErrors({ _: `Not saved: ${e.message}.` }); return }
      const demo = demoMessage(e)
      if (demo) { setErrors({ _: demo }); return }
      if (e instanceof ApiError && e.status === 422) {
        const fe = fieldErrors(e) // summary too: a field the form does not show would otherwise fail silently
        setErrors({ ...fe, _: `Not accepted: ${Object.entries(fe).map(([k, m]) => `${k} (${m})`).join(', ')}` }); setStep(2); return
      }
      setErrors({ _: e instanceof ApiError && e.status === 503 ? 'Cannot verify consent while the record store is down. Analysis is blocked.' : (e as Error).message })
    } finally {
      setBusy(false)
    }
  }

  const canNext = step === 0 ? mode !== null : step === 1 ? consentOk : true
  return (
    <div>
      <PageTitle>New case · {patient.patient.name} <span className="font-mono text-base font-normal text-muted">{patient.patient.hn}</span></PageTitle>
      <StepList step={step} go={setStep} />
      {step === 0 && <ModeStep mode={mode} setMode={setMode} />}
      {step === 1 && <ConsentStep patientId={pid} onReady={onReady} />}
      {step === 2 && mode && <InputsForm mode={mode} values={values} dates={dates} errors={errors}
        onChange={(k, v) => setValues((old) => ({ ...old, [k]: v }))} />}
      {step === 2 && <ErrorText>{errors._}</ErrorText>}
      {step === 3 && (result && !result.quality.accept ? <RetakeCard r={result} preview={preview} onRetake={() => pick(null)} /> : (
        <div className="flex max-w-3xl flex-col gap-4">
          <div className="flex flex-col items-start gap-3 rounded-lg border-2 border-dashed border-rule-strong bg-surface p-6">
            <label htmlFor="photo" className="font-medium">Fundus photo</label>
            <input id="photo" type="file" accept="image/jpeg,image/png" disabled={busy} onChange={(e) => pick(e.target.files?.[0] ?? null)}
              className="file:btn-secondary file:mr-4" />
            <p className="text-sm text-muted">JPEG or PNG, up to 20 MB</p>
            {preview && <img src={preview} alt="Selected fundus photo" className="h-40 w-40 bg-stage object-contain" />}
          </div>
          <div className="flex flex-wrap gap-2">
            {demoImages.map((d) => {
              const same = demoImages.filter((x) => x.label === d.label)
              const label = same.length > 1 ? `${d.label} ${same.indexOf(d) + 1}` : d.label
              return (
                <div key={d.name} className="flex flex-col items-start gap-1">
                  <button className="btn-secondary" disabled={busy} onClick={() => pickCached(d.name)}>Cached: {label} <span className="font-mono text-xs text-muted">{d.name}</span></button>
                  <span className="max-w-xs text-xs text-muted"><b className="font-medium text-ink">{d.licence}</b>. <span className="line-clamp-2" title={d.source}>{d.source}</span></span>
                </div>
              )
            })}
          </div>
          <ErrorText>{errors._}</ErrorText>
          <div>
            <button className="btn-primary" disabled={!file || busy} onClick={analyse}>
              {busy ? <><LoaderCircle size={20} className="animate-spin" aria-hidden />Analysing…</> : 'Analyse photo'}
            </button>
            {!file && <p className="mt-1 text-sm text-muted">Choose a photo first.</p>}
            {busy && <p className="mt-1 text-sm text-muted" role="status">An uncached photo can take up to about 2 minutes to analyse.</p>}
          </div>
        </div>
      ))}
      {step === 4 && result && <ResultView r={result} fundus={preview} patient={patient.patient} status={result.status}
        overlays={Object.fromEntries(Object.entries(result.overlays ?? {}).filter(([, v]) => v).map(([k, v]) => [k, `data:image/png;base64,${v}`]))}
        layers={layers} setLayers={setLayers} />}
      {step < 3 && (
        <div className="mt-8 flex max-w-4xl justify-between border-t border-rule pt-4">
          <button className="btn-secondary" disabled={step === 0} onClick={() => setStep(step - 1)}>Back</button>
          <div className="text-right">
            <button className="btn-primary" disabled={!canNext} onClick={next}>Continue</button>
            {!canNext && <p className="mt-1 text-sm text-muted">{step === 0 ? 'Choose a mode.' : 'Consent must be on file.'}</p>}
          </div>
        </div>
      )}
    </div>
  )
}

export default function NewCase({ patientId }: { patientId?: string }): ReactNode {
  const { data, error } = useLoad(() => (patientId ? api.patient(patientId) : Promise.resolve(null)), [patientId])
  if (!patientId) return <><PageTitle>New case: choose a patient</PageTitle><PatientSearch hrefFor={(id) => `/new/${id}`} /></>
  if (error) return <ErrorText>{error}</ErrorText>
  return data ? <Wizard patient={data} /> : <p>Loading…</p>
}
