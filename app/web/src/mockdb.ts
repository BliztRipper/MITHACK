// shortcut: browser-only test DB used when /api is unreachable (the hosted API is down); writes live in localStorage,
// so each browser has its own copy. Data: public/mockdb, recorded from the real API by scripts/capture-mockdb.py.
// Delete this file and its two hooks in api.ts once the API is hosted again.
import type { CaseRecord, CaseResult, Consent, DemoImage, Health, PatientDetail, QueueItem, Review, User } from './api'

interface Seed {
  health: Health; users: Record<string, User>; demo_images: DemoImage[]; about: unknown; monitoring: unknown; audit: unknown
  patients: Record<string, PatientDetail>
  results: Record<string, CaseResult> // "<demo photo>|<mode>" -> what POST /cases returned for it
  cases: Record<string, { record: CaseRecord; history: unknown; summary: Record<string, unknown> }>
  media: Record<string, string> // media id -> file under /mockdb/media
}
interface State { user: User | null; patients: Record<string, PatientDetail>; cases: Record<string, CaseRecord>; template: Record<string, string> }

const KEY = 'retina-mockdb-v1'
let seed: Seed | null = null
let state: State
export let active = false

async function load(): Promise<void> {
  if (seed) return
  seed = (await (await fetch('/mockdb/db.json')).json()) as Seed
  const saved = localStorage.getItem(KEY)
  state = saved ? JSON.parse(saved) as State
    : { user: null, patients: seed.patients, cases: Object.fromEntries(Object.entries(seed.cases).map(([id, c]) => [id, c.record])), template: {} }
}
const save = (): void => localStorage.setItem(KEY, JSON.stringify(state))

export const mockMediaUrl = (id: string): string => `/mockdb/media/${seed?.media[id] ?? id}`
export const mockDemoImageUrl = (name: string): string => `/mockdb/demo-images/${name}`

const reply = (data: unknown, status = 200): Response =>
  new Response(JSON.stringify(status < 400 ? data : { detail: data }), { status, headers: { 'Content-Type': 'application/json' } })

function queueItem(c: CaseRecord): QueueItem {
  const { report_id, patient_id, mode, status, level, issued, conclusion, inputs, media } = c
  const waiting = issued ? Math.round((Date.now() - Date.parse(issued)) / 6000) / 10 : null
  return { report_id, patient_id, mode, status, level, issued, waiting_minutes: waiting, conclusion, inputs, media }
}

function createCase(f: FormData): Response {
  const pid = String(f.get('patient_id')), mode = String(f.get('mode'))
  const p = state.patients[pid]
  if (!p) return reply('patient not found', 404)
  if (!p.consent.care) return reply('no care consent recorded for this patient', 403)
  const tpl = seed!.results[`${(f.get('image') as File).name}|${mode}`]
  if (!tpl) return reply({ code: 'demo_photo_only' }, 422)
  const id = `t${Date.now()}`, now = new Date().toISOString().replace(/\.\d+Z$/, '+00:00')
  const result = { ...tpl, case_id: id, report_id: id, patient_id: pid }
  state.cases[id] = { ...structuredClone(seed!.cases[tpl.report_id!].record), report_id: id, patient_id: pid, issued: now,
    status: 'preliminary', patient: p.patient, analysis: result, reviews: [], can_sign: true }
  state.template[id] = tpl.report_id!
  p.cases.unshift({ report_id: id, date: now, mode: mode as CaseRecord['mode'], status: 'preliminary', result: tpl.conclusion, readable: true })
  save()
  return reply(result)
}

function review(id: string, body: Record<string, unknown>, action: 'sign' | 'amend'): Response {
  const c = state.cases[id]
  if (!c) return reply('case not found', 404)
  if (action === 'sign' && c.status !== 'preliminary') return reply('already signed: use amend', 409)
  if (action === 'amend' && c.status === 'preliminary') return reply('not signed yet: sign it instead', 409)
  if (action === 'sign' && c.mode === 'emergency' && body.crao == null) return reply('state whether CRAO is clinically confirmed', 422)
  c.status = action === 'sign' ? 'final' : 'amended'
  if (action === 'amend' || body.decision === 'override') c.conclusion = String(body.finding)
  c.reviews.push({ action, ai_conclusion: c.analysis.conclusion, finding: null, reason_text: null, ...body,
    by: `Practitioner/${state.user?.username}`, user: state.user?.username ?? '', at: new Date().toISOString() } as Review)
  c.can_sign = false
  const prior = state.patients[c.patient_id]?.cases.find((x) => x.report_id === id)
  if (prior) prior.status = c.status
  save()
  return reply({ ...queueItem(c), reviews: c.reviews })
}

function setConsent(pid: string, consent: Consent): Response {
  const p = state.patients[pid]
  if (!p) return reply('patient not found', 404)
  p.consent = consent
  save()
  return reply(consent)
}

/** Answers like the real API (same paths and shapes) from the test DB. */
export async function mockFetch(method: string, path: string, body?: unknown): Promise<Response> {
  active = true
  await load()
  const s = seed!, b = (body ?? {}) as Record<string, unknown>
  const [route, query] = path.split('?')
  const seg = route.split('/').filter(Boolean)
  const key = `${method} /${seg.map((x, i) => (i === 1 && /^t?\d+$/.test(x) ? ':id' : x)).join('/')}`
  const id = seg[1], tplId = (rid: string): string => state.template[rid] ?? rid
  switch (key) {
    case 'GET /health': return reply(s.health)
    case 'POST /auth/login': {
      const ok = s.health.demo_accounts?.some((a) => a.username === b.username && a.password === b.password)
      if (!ok) return reply('wrong username or password', 401)
      state.user = s.users[String(b.username)]
      save()
      return reply(state.user)
    }
    case 'POST /auth/logout': state.user = null; save(); return reply({ ok: true })
    case 'GET /auth/me': return state.user ? reply(state.user) : reply('not signed in', 401)
    case 'GET /demo-images': return reply(s.demo_images)
    case 'GET /about': return reply(s.about)
    case 'GET /monitoring': return reply(s.monitoring)
    case 'GET /audit': return reply(s.audit)
    case 'GET /patients': return reply(Object.values(state.patients).map((p) => p.patient).sort((a, b) => (a.hn ?? '~').localeCompare(b.hn ?? '~')))
    case 'POST /patients/search': {
      const q = String(b.q).trim().toLowerCase()
      return reply(Object.values(state.patients).map((p) => p.patient)
        .filter((p) => p.name.toLowerCase().includes(q) || (p.hn ?? '').toLowerCase().includes(q)))
    }
    case 'GET /patients/:id': return state.patients[id] ? reply(state.patients[id]) : reply('patient not found', 404)
    case 'GET /patients/:id/consent': return state.patients[id] ? reply(state.patients[id].consent) : reply('patient not found', 404)
    case 'POST /patients/:id/consent': return setConsent(id, { care: true, model_improvement: Boolean(b.model_improvement) })
    case 'POST /patients/:id/withdraw': return setConsent(id, { care: false, model_improvement: false })
    case 'POST /cases': return createCase(body as FormData)
    case 'GET /review/queue': return reply(Object.values(state.cases).filter((c) => c.status === 'preliminary')
      .map((c) => ({ ...queueItem(c), patient: { name: c.patient.name, hn: c.patient.hn } }))
      .sort((x, y) => Number(x.mode !== 'emergency') - Number(y.mode !== 'emergency') || (x.issued ?? '').localeCompare(y.issued ?? '')))
    case 'GET /cases/:id': return state.cases[id] ? reply(state.cases[id]) : reply('case not found', 404)
    case 'POST /cases/:id/sign': return review(id, b, 'sign')
    case 'POST /cases/:id/amend': return review(id, b, 'amend')
    case 'GET /cases/:id/history': return reply(s.cases[tplId(id)]?.history ?? [])
    case 'GET /cases/:id/summary': {
      const lang = new URLSearchParams(query).get('lang') ?? 'en'
      return reply(s.cases[tplId(id)]?.summary[lang] ?? { lang, text: [] })
    }
    case 'POST /cases/:id/incident':
      return reply({ id: `f${Date.now()}`, status: 'open', metric: null, text: b.description, case: id, opened: new Date().toISOString() })
    default: return method === 'POST' ? reply({ ok: true }) : reply('not in the test DB', 404)
  }
}
