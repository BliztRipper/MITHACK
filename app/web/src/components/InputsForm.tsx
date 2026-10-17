import type { ReactNode } from 'react'
import type { Mode, PatientDetail } from '../api'
import { ageOf, ErrorText, fmtDate } from './ui'

// Plausibility limits mirror the API (routes/cases.py); the API re-checks and its 422 maps back to these fields.
interface NumField { key: string; label: string; unit?: string; min: number; max: number; required?: boolean; step?: number }
const NUMBERS: NumField[] = [
  { key: 'age', label: 'Age', unit: 'years', min: 18, max: 110, required: true, step: 1 },
  { key: 'sbp', label: 'Systolic blood pressure', unit: 'mmHg', min: 60, max: 260, required: true },
  { key: 'dbp', label: 'Diastolic blood pressure', unit: 'mmHg', min: 30, max: 160 },
  { key: 'tc', label: 'Total cholesterol', unit: 'mg/dL', min: 50, max: 500, required: true },
  { key: 'hdl', label: 'HDL cholesterol', unit: 'mg/dL', min: 10, max: 200, required: true },
  { key: 'ldl', label: 'LDL cholesterol (optional)', unit: 'mg/dL', min: 10, max: 400 },
]
// Equation inputs: explicit yes/no, never defaulted, so a forgotten answer cannot silently lower the risk.
const ANSWERS: [string, string][] = [
  ['diabetes', 'Diabetes?'], ['treated_htn', 'On treatment for hypertension?'], ['ascvd', 'Known atherosclerotic CVD?'],
  ['african_american', 'Race group African American? (used by PCE only)'],
]

export type Values = Record<string, string | boolean | null>

/** Initial values: Screening fields pre-filled from the record (with dates); Emergency answers never defaulted. */
export function initialValues(mode: Mode, d: PatientDetail): { values: Values; dates: Record<string, string> } {
  if (mode === 'emergency') return { values: { hours_since_onset: '', onset_unknown: false, sudden_painless_monocular: null, gca_symptoms: null }, dates: {} }
  const values: Values = { age: String(ageOf(d.patient.birth_date) ?? ''), sex: d.patient.gender === 'male' || d.patient.gender === 'female' ? d.patient.gender : '',
    smoking: '', clinical_enhancers: '' }
  const dates: Record<string, string> = {}
  for (const f of NUMBERS) values[f.key] ??= ''
  for (const [k] of ANSWERS) values[k] = null
  values.arcus_senilis = false // a clinical observation, not an equation input
  for (const [k, v] of Object.entries(d.latest)) {
    if (!v) continue
    values[k] = typeof v.value === 'boolean' ? v.value : String(v.value)
    dates[k] = v.date
  }
  if (!['never', 'former', 'current'].includes(String(values.smoking))) values.smoking = ''
  return { values, dates }
}

/** Client-side check; returns {field: message}. */
export function validate(mode: Mode, v: Values): Record<string, string> {
  const e: Record<string, string> = {}
  if (mode === 'emergency') {
    if (!v.onset_unknown) {
      const h = Number(v.hours_since_onset)
      if (v.hours_since_onset === '' || !Number.isFinite(h) || h < 0 || h > 8760) e.hours_since_onset = 'Enter hours since onset (0–8760), or tick "Onset unknown"'
    }
    if (v.sudden_painless_monocular === null) e.sudden_painless_monocular = 'Answer yes or no'
    if (v.gca_symptoms === null) e.gca_symptoms = 'Answer yes or no'
    return e
  }
  for (const f of NUMBERS) {
    const s = String(v[f.key] ?? '')
    if (s === '') { if (f.required) e[f.key] = 'Required'; continue }
    const n = Number(s)
    if (!Number.isFinite(n) || n < f.min || n > f.max) e[f.key] = `Accepted ${f.min}–${f.max}${f.unit ? ` ${f.unit}` : ''}`
  }
  if (!v.sex) e.sex = 'Choose male or female'
  if (!v.smoking) e.smoking = 'Choose smoking status'
  for (const [k] of ANSWERS) if (v[k] === null) e[k] = 'Answer yes or no'
  if (String(v.clinical_enhancers).split('\n').filter((s) => s.trim()).length > 10) e.clinical_enhancers = 'At most 10 enhancers'
  return e
}

/** The JSON `inputs` form field for POST /cases. */
export function toInputs(mode: Mode, v: Values): Record<string, unknown> {
  if (mode === 'emergency')
    return { hours_since_onset: v.onset_unknown ? null : Number(v.hours_since_onset), sudden_painless_monocular: v.sudden_painless_monocular, gca_symptoms: v.gca_symptoms }
  const out: Record<string, unknown> = { sex: v.sex, smoking: v.smoking }
  for (const f of NUMBERS) if (v[f.key] !== '') out[f.key] = Number(v[f.key])
  for (const [k] of ANSWERS) out[k] = v[k]
  out.arcus_senilis = Boolean(v.arcus_senilis)
  out.clinical_enhancers = String(v.clinical_enhancers).split('\n').map((s) => s.trim()).filter(Boolean)
  return out
}

interface Props { mode: Mode; values: Values; dates: Record<string, string>; errors: Record<string, string>; onChange: (k: string, v: string | boolean | null) => void }

function YesNo({ name, label, value, error, onChange }: { name: string; label: string; value: string | boolean | null; error?: string; onChange: Props['onChange'] }): ReactNode {
  return (
    <fieldset aria-describedby={error ? `${name}-err` : undefined}>
      <legend className="mb-1">{label}</legend>
      <div className="flex gap-6">
        {([true, false] as const).map((b) => (
          <label key={String(b)} className="flex items-center gap-2">
            <input type="radio" className="check" name={name} checked={value === b} onChange={() => onChange(name, b)} />{b ? 'Yes' : 'No'}
          </label>
        ))}
      </div>
      <ErrorText id={`${name}-err`}>{error}</ErrorText>
    </fieldset>
  )
}

export default function InputsForm({ mode, values: v, dates, errors, onChange }: Props): ReactNode {
  if (mode === 'emergency')
    return (
      <div className="flex max-w-xl flex-col gap-6">
        <div>
          <label htmlFor="hours_since_onset" className="mb-1 block">Hours since onset of vision loss</label>
          <div className="flex items-center gap-2">
            <input id="hours_since_onset" className="input max-w-40" type="number" min={0} step="0.5" inputMode="decimal" disabled={Boolean(v.onset_unknown)}
              value={String(v.hours_since_onset)} onChange={(e) => onChange('hours_since_onset', e.target.value)}
              aria-invalid={Boolean(errors.hours_since_onset)} aria-describedby={errors.hours_since_onset ? 'hours-err' : undefined} />
            <span className="text-muted">h</span>
          </div>
          <label className="mt-2 flex items-center gap-2">
            <input type="checkbox" className="check" checked={Boolean(v.onset_unknown)} onChange={(e) => { onChange('onset_unknown', e.target.checked); onChange('hours_since_onset', '') }} />
            Onset unknown
          </label>
          <ErrorText id="hours-err">{errors.hours_since_onset}</ErrorText>
        </div>
        <YesNo name="sudden_painless_monocular" label="Sudden, painless, one eye?" value={v.sudden_painless_monocular} error={errors.sudden_painless_monocular} onChange={onChange} />
        <YesNo name="gca_symptoms" label="Jaw claudication, scalp tenderness, or new headache (GCA symptoms)?" value={v.gca_symptoms} error={errors.gca_symptoms} onChange={onChange} />
      </div>
    )

  const select = (key: string, label: string, opts: string[]): ReactNode => (
    <div>
      <label htmlFor={key} className="mb-1 block">{label}</label>
      <select id={key} className="input" value={String(v[key])} onChange={(e) => onChange(key, e.target.value)}
        aria-invalid={Boolean(errors[key])} aria-describedby={errors[key] ? `${key}-err` : undefined}>
        <option value="">Choose…</option>
        {opts.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
      {dates[key] && <p className="mt-1 text-sm text-muted">from record, {fmtDate(dates[key])}</p>}
      <ErrorText id={`${key}-err`}>{errors[key]}</ErrorText>
    </div>
  )

  return (
    <div className="grid max-w-4xl gap-4 lg:grid-cols-2">
      {select('sex', 'Sex', ['male', 'female'])}
      {select('smoking', 'Smoking', ['never', 'former', 'current'])}
      {NUMBERS.map((f) => (
        <div key={f.key}>
          <label htmlFor={f.key} className="mb-1 block">{f.label}{f.required ? ' (required)' : ''}</label>
          <div className="relative">
            <input id={f.key} className="input pr-16" type="number" inputMode="decimal" step={f.step ?? 'any'} value={String(v[f.key])}
              onChange={(e) => onChange(f.key, e.target.value)} aria-invalid={Boolean(errors[f.key])} aria-describedby={errors[f.key] ? `${f.key}-err` : undefined} />
            {f.unit && <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-sm text-muted">{f.unit}</span>}
          </div>
          {dates[f.key] && <p className="mt-1 text-sm text-muted">from record, {fmtDate(dates[f.key])}</p>}
          <ErrorText id={`${f.key}-err`}>{errors[f.key]}</ErrorText>
        </div>
      ))}
      {ANSWERS.map(([k, label]) => (
        <div key={k}>
          <YesNo name={k} label={`${label} (required)`} value={v[k]} error={errors[k]} onChange={onChange} />
          {dates[k] && <p className="mt-1 text-sm text-muted">from record, {fmtDate(dates[k])}</p>}
        </div>
      ))}
      <label className="flex items-center gap-2 lg:col-span-2">
        <input type="checkbox" className="check" checked={Boolean(v.arcus_senilis)} onChange={(e) => onChange('arcus_senilis', e.target.checked)} />Arcus senilis observed
        {dates.arcus_senilis && <span className="text-sm text-muted">(from record, {fmtDate(dates.arcus_senilis)})</span>}
      </label>
      <div className="lg:col-span-2">
        <label htmlFor="clinical_enhancers" className="mb-1 block">Clinical risk enhancers (one per line, optional)</label>
        <textarea id="clinical_enhancers" rows={3} className="input h-auto py-2" value={String(v.clinical_enhancers)}
          onChange={(e) => onChange('clinical_enhancers', e.target.value)} aria-describedby={errors.clinical_enhancers ? 'enh-err' : undefined} />
        <ErrorText id="enh-err">{errors.clinical_enhancers}</ErrorText>
      </div>
    </div>
  )
}
