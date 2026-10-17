// One client for the FastAPI backend (shapes: .superpowers/sdd/tasks/task-5-report.md). Vite proxies /api.

export type Role = 'gp' | 'reviewer' | 'admin'
export type Mode = 'screening' | 'emergency'
export type Level = 'STROKE_PATHWAY' | 'URGENT' | 'ESCALATE' | 'RETAKE' | 'ROUTINE'
export type Band = 'unlikely' | 'uncertain' | 'likely'
export type OverlayKind = 'vessel' | 'artery_vein' | 'disc' | 'heatmap'

export interface User { username: string; role: Role; name: string }
export interface PatientSummary { id: string; hn: string | null; name: string; gender: string | null; birth_date: string | null }
export interface Consent { care: boolean; model_improvement: boolean }
export interface Dated { value: number | boolean | string; date: string }
export interface PriorCase { report_id: string; date: string | null; mode: Mode; status: string; result: string | null }
export interface PatientDetail {
  patient: PatientSummary
  consent: Consent
  latest: Partial<Record<'sbp' | 'dbp' | 'tc' | 'hdl' | 'ldl' | 'smoking' | 'arcus_senilis', Dated>>
  cases: PriorCase[]
}

export interface ModelInfo { model: string; version: string; calibration_date: string | null; [k: string]: unknown }
export interface Crao {
  status: string; probability: number | null; band: Band | null; p_low: number; p_high: number; model: ModelInfo | null
}
export interface Triage { level: Level; actions: string[]; reasons: string[] }
export interface Measure { value: number | null; flag: string | null; reference?: [number, number]; reference_status?: string; unit?: string; reason?: string; note?: string }
export interface Risk {
  pce: { label: string; risk: number | null; band: string | null; not_valid: string | null; notes: string[]; suggestion: string | null; suggestion_label: string }
  bypass: string | null
  htn_stage1: string | null
  enhancers: { retinal: string[]; clinical: string[]; not_assessed: string | null; note: string | null }
  arcus: string | null
}
export interface CaseResult {
  case_id: string; report_id: string | null; saved: boolean; save_error: string | null; status: string; label: string
  mode: Mode; patient_id: string; cached: boolean; model_version: string
  quality: { accept: boolean; score: number; reasons: string[]; parts: Record<string, number | boolean> }
  segmentation: { disc_found: boolean; disc_centre: [number, number] | null; disc_diameter: number | null } | null
  inputs: Record<string, unknown>
  conclusion: string
  explanation: { region: string | null; sentences: string[] }
  overlays?: Record<OverlayKind, string | null> // base64 PNG, only on POST /cases
  crao?: Crao; triage?: Triage
  measurements?: { avr: Measure; crae: Measure; crve: Measure } | null
  risk?: Risk
}
export interface QueueItem {
  report_id: string; patient_id: string; mode: Mode; status: string; level: string | null; issued: string | null
  waiting_minutes: number | null; conclusion: string | null; inputs: Record<string, unknown> | null
  media: { id: string; kind: 'fundus' | OverlayKind }[]
  patient?: { name: string; hn: string | null } // queue only
}
export interface SignedLayers { visible: OverlayKind[]; opacity: number }
export interface Review {
  action: 'sign' | 'amend'; decision?: 'confirm' | 'override'; finding: string | null; reason?: string | null
  reason_text: string | null; crao?: boolean | null; ai_conclusion?: string | null; layers?: SignedLayers | null; by: string; user: string; at: string
}
export interface CaseRecord extends QueueItem {
  label: string; patient: PatientSummary; analysis: CaseResult; reviews: Review[]; can_sign: boolean
}
export interface SignBody {
  decision: 'confirm' | 'override'; finding?: string; reason?: string; reason_text?: string; crao?: boolean; layers: SignedLayers
}
export interface Rate { value: number | null; n: number }
export interface VersionMetrics {
  version: string; cases: number; by_mode: Record<string, number>; quality_rejection_rate: Rate; uncertain_rate: Rate
  agreement_rate: Rate; override_reasons: Record<string, number>; triage_levels: Record<string, number>
}
export interface FlagView { id: string; status: string; metric: string | null; text: string; case: string | null; opened: string | null }
export interface Monitoring {
  period_days: number; current_version: string; metrics: VersionMetrics[]
  calibration: { status: 'insufficient data'; n: number; needed: number; text: string }
    | { status: 'ok'; n: number; needed: number; bands: Record<Band, { n: number; mean_p: number | null; observed_crao_rate: number | null }> }
  alerts: FlagView[]; incidents: FlagView[]
}
export interface ConfigValue { value: unknown; status: string; source?: string }
export interface About {
  config: Record<'triage' | 'risk' | 'monitoring', Record<string, ConfigValue>>
  crao_thresholds: { p_low: number; p_high: number; source: string }
  model: ModelInfo | null; model_status: string
}
export interface AuditRow { id: string; time: string; user: string; role: string; action: string; outcome: string; resource: string }

export class ApiError extends Error {
  status: number
  detail: unknown
  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : (detail as { message?: string })?.message ?? `request failed (${status})`)
    this.status = status
    this.detail = detail
  }
}

/** Fire on 401 (session gone) and 503 (record store down) so the shell can react. */
export const events = new EventTarget()

async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  const init: RequestInit = { method, credentials: 'same-origin' }
  if (body instanceof FormData) init.body = body
  else if (body !== undefined) {
    init.body = JSON.stringify(body)
    init.headers = { 'Content-Type': 'application/json' }
  }
  const r = await fetch(`/api${path}`, init)
  if (r.status === 401 && path !== '/auth/login') events.dispatchEvent(new Event('unauthorized'))
  if (r.status === 503) events.dispatchEvent(new Event('store-down'))
  const data = r.headers.get('content-type')?.includes('json') ? await r.json() : null
  if (!r.ok) throw new ApiError(r.status, data?.detail ?? r.statusText)
  return data as T
}

/** 422 detail -> {field: message}; a plain string detail lands under "_". */
export function fieldErrors(e: unknown): Record<string, string> {
  if (!(e instanceof ApiError)) return { _: String(e) }
  if (Array.isArray(e.detail))
    return Object.fromEntries(e.detail.map((d: { loc: unknown[]; msg: string }) => [String(d.loc.at(-1)), d.msg]))
  return { _: e.message }
}

export const mediaUrl = (id: string): string => `/api/media/${id}`

export const api = {
  login: (username: string, password: string) => call<User>('POST', '/auth/login', { username, password }),
  logout: () => call<{ ok: true }>('POST', '/auth/logout'),
  me: () => call<User>('GET', '/auth/me'),
  health: () => call<{ api: string; record_store: 'available' | 'unavailable' }>('GET', '/health'),
  about: () => call<About>('GET', '/about'),
  search: (q: string) => call<PatientSummary[]>('POST', '/patients/search', { q }),
  patient: (id: string) => call<PatientDetail>('GET', `/patients/${id}`),
  consent: (id: string) => call<Consent>('GET', `/patients/${id}/consent`),
  recordConsent: (id: string, b: { care: true; model_improvement: boolean; retention_years: number; right_to_withdraw_explained: true }) =>
    call<Consent>('POST', `/patients/${id}/consent`, b),
  withdraw: (id: string) => call<Consent>('POST', `/patients/${id}/withdraw`),
  createCase: (f: FormData) => call<CaseResult>('POST', '/cases', f),
  queue: () => call<QueueItem[]>('GET', '/review/queue'),
  case: (id: string) => call<CaseRecord>('GET', `/cases/${id}`),
  sign: (id: string, b: SignBody) => call<QueueItem & { reviews: Review[] }>('POST', `/cases/${id}/sign`, b),
  amend: (id: string, b: { finding: string; reason_text: string }) => call<QueueItem>('POST', `/cases/${id}/amend`, b),
  history: (id: string) => call<{ version: string; status: string; conclusion: string | null; updated: string }[]>('GET', `/cases/${id}/history`),
  summary: (id: string, lang: 'en' | 'th') => call<{ lang: string; text: string[] }>('GET', `/cases/${id}/summary?lang=${lang}`),
  incident: (id: string, description: string) => call<FlagView>('POST', `/cases/${id}/incident`, { description }),
  monitoring: (days: number) => call<Monitoring>('GET', `/monitoring?days=${days}`),
  acknowledge: (id: string, note: string) => call<FlagView>('POST', `/monitoring/alerts/${id}/acknowledge`, { note }),
  closeIncident: (id: string, note: string) => call<FlagView>('POST', `/monitoring/incidents/${id}/close`, { note }),
  audit: (days: number) => call<AuditRow[]>('GET', `/audit?days=${days}`),
}
