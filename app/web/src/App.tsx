import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { DatabaseZap, LogOut, Menu } from 'lucide-react'
import { api, events, type DemoAccount, type Role, type User } from './api'
import { Link, navigate, Session, usePath } from './components/ui'
import About from './pages/About'
import Audit from './pages/Audit'
import Case from './pages/Case'
import Login from './pages/Login'
import Monitoring from './pages/Monitoring'
import NewCase from './pages/NewCase'
import Patient from './pages/Patient'
import Patients from './pages/Patients'
import Queue from './pages/Queue'

interface Route { path: RegExp; roles: Role[]; nav?: string; href?: string; page: (m: string[]) => ReactNode }

// Order = rail order. A link shows only for roles the API would not refuse (design §3.2).
const CLIN: Role[] = ['gp', 'reviewer']
const ROUTES: Route[] = [
  { path: /^\/patients$/, roles: CLIN, nav: 'Patients', href: '/patients', page: () => <Patients /> },
  { path: /^\/patients\/([A-Za-z0-9.-]{1,64})$/, roles: CLIN, page: ([id]) => <Patient key={id} id={id} /> },
  { path: /^\/new$/, roles: CLIN, nav: 'New case', href: '/new', page: () => <NewCase /> },
  { path: /^\/new\/([A-Za-z0-9.-]{1,64})$/, roles: CLIN, page: ([id]) => <NewCase key={id} patientId={id} /> },
  { path: /^\/cases\/([A-Za-z0-9.-]{1,64})$/, roles: CLIN, page: ([id]) => <Case key={id} id={id} /> },
  { path: /^\/queue$/, roles: CLIN, nav: 'Review queue', href: '/queue', page: () => <Queue /> },
  { path: /^\/monitoring$/, roles: ['reviewer', 'admin'], nav: 'Monitoring', href: '/monitoring', page: () => <Monitoring /> },
  { path: /^\/audit$/, roles: ['admin'], nav: 'Audit', href: '/audit', page: () => <Audit /> },
  { path: /^\/about$/, roles: ['gp', 'reviewer', 'admin'], nav: 'About', href: '/about', page: () => <About /> },
]

function Banner(): ReactNode {
  return (
    <div role="status" aria-live="polite" className="iris-in flex items-center gap-2 border-b-2 border-triage-urgent bg-system-warn-tint px-4 py-2 font-medium text-ink print:hidden">
      <DatabaseZap size={20} aria-hidden />
      Record store unavailable. Results still display, but nothing can be saved or signed until it is back.
    </div>
  )
}

function DemoBanner(): ReactNode {
  return (
    <div role="status" className="sticky top-0 z-30 border-b-2 border-accent bg-accent-tint px-4 py-2 text-center font-medium text-ink print:hidden">
      Demo: synthetic patients, not a medical device, data resets daily
    </div>
  )
}

function Nav({ user, path, onSignOut }: { user: User; path: string; onSignOut: () => void }): ReactNode {
  const links = ROUTES.filter((r) => r.nav && r.roles.includes(user.role))
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-4 text-base font-semibold">Retina CVD/CRAO</div>
      <nav aria-label="Main" className="flex-1">
        <ul className="flex flex-col gap-1 px-2">
          {links.map((r) => {
            const active = path === r.href || (r.href !== '/' && path.startsWith(r.href + '/'))
            return (
              <li key={r.href}>
                <Link href={r.href!} aria-current={active ? 'page' : undefined}
                  className={`block rounded-md px-3 py-2 ${active ? 'bg-accent-tint font-medium text-accent' : 'text-ink hover:bg-sunken'}`}>
                  {r.nav}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
      <div className="border-t border-rule px-4 py-4">
        <div className="font-medium">{user.name}</div>
        <div className="mb-3 text-xs uppercase tracking-wide text-muted">{user.role}</div>
        <button className="btn-secondary w-full" onClick={onSignOut}><LogOut size={20} aria-hidden />Sign out</button>
      </div>
    </div>
  )
}

export default function App(): ReactNode {
  const path = usePath()
  const [user, setUser] = useState<User | null | undefined>(undefined) // undefined = still checking the cookie
  const [storeDown, setStoreDown] = useState(false)
  const [demo, setDemo] = useState<DemoAccount[] | null>(null) // null = not demo mode
  const [menuAt, setMenuAt] = useState<string | null>(null) // the narrow-screen menu closes itself on navigation

  const checkHealth = useCallback(() => {
    api.health().then((h) => { setStoreDown(h.record_store === 'unavailable'); setDemo(h.demo ? h.demo_accounts ?? [] : null) }).catch(() => setStoreDown(true))
  }, [])

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null))
    checkHealth()
    const t = setInterval(checkHealth, 30_000)
    const out = (): void => setUser(null)
    events.addEventListener('unauthorized', out)
    events.addEventListener('store-down', checkHealth)
    return () => {
      clearInterval(t)
      events.removeEventListener('unauthorized', out)
      events.removeEventListener('store-down', checkHealth)
    }
  }, [checkHealth])

  const menuOpen = menuAt === path
  const toggleRef = useRef<HTMLButtonElement>(null)
  const railRef = useRef<HTMLElement>(null)
  useEffect(() => { // narrow-screen menu: focus moves in on open; Escape closes it and returns focus to the toggle
    if (!menuOpen) return
    railRef.current?.querySelector<HTMLElement>('a, button')?.focus()
    const onKey = (ev: KeyboardEvent): void => {
      if (ev.code !== 'Escape' && ev.key !== 'Escape') return
      setMenuAt(null)
      toggleRef.current?.focus()
    }
    addEventListener('keydown', onKey)
    return () => removeEventListener('keydown', onKey)
  }, [menuOpen])
  if (user === undefined) return null
  if (user === null) return <>{demo && <DemoBanner />}{storeDown && <Banner />}<Login accounts={demo ?? []} onLogin={(u) => { setUser(u); navigate('/') }} /></>

  const signOut = (): void => { api.logout().finally(() => { setUser(null); navigate('/') }) }
  const pathname = path.split('?')[0]
  const home = ROUTES.find((r) => r.nav && r.roles.includes(user.role))
  if (pathname === '/' && home) { navigate(home.href!); return null }
  const route = ROUTES.find((r) => r.path.test(pathname))
  const body = !route ? <p>Page not found.</p>
    : !route.roles.includes(user.role) ? <p>Your role ({user.role}) cannot open this page.</p>
    : route.page(pathname.match(route.path)!.slice(1))

  return (
    <Session.Provider value={{ user, storeDown }}>
      <div className="flex min-h-screen flex-col">
        {demo && <DemoBanner />}
        {storeDown && <Banner />}
        <header className="flex items-center justify-between border-b border-rule bg-surface px-4 py-2 lg:hidden print:hidden">
          <span className="font-semibold">Retina CVD/CRAO</span>
          <button ref={toggleRef} className="btn-secondary" aria-expanded={menuOpen} aria-controls="rail" onClick={() => setMenuAt(menuOpen ? null : path)}>
            <Menu size={20} aria-hidden />Menu
          </button>
        </header>
        <div className="flex flex-1">
          <aside id="rail" ref={railRef} className={`${menuOpen ? 'block' : 'hidden'} fixed inset-y-0 left-0 z-40 w-56 overflow-y-auto overscroll-contain border-r border-rule bg-surface lg:static lg:block print:hidden`}>
            <Nav user={user} path={pathname} onSignOut={signOut} />
          </aside>
          <main className="min-w-0 flex-1 px-4 py-6 lg:px-8 print:p-0">
            <div className="mx-auto max-w-[1440px]">{body}</div>
          </main>
        </div>
      </div>
    </Session.Provider>
  )
}
