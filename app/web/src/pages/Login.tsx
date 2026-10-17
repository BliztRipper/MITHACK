import { useState, type ReactNode } from 'react'
import { api, ApiError, type User } from '../api'
import { ErrorText } from '../components/ui'

export default function Login({ onLogin }: { onLogin: (u: User) => void }): ReactNode {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      onLogin(await api.login(username, password))
    } catch (err) {
      setError(err instanceof ApiError && err.status === 401 ? 'Wrong username or password.' : 'Sign-in failed. Is the API running?')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <form onSubmit={submit} className="card w-full max-w-sm flex flex-col gap-4 p-6" aria-describedby={error ? 'login-error' : undefined}>
        <div>
          <h1 className="text-xl font-semibold">Retina CVD/CRAO</h1>
          <p className="text-muted">Fundus photo to a signed next action: CVD risk screening and sudden vision loss triage.</p>
        </div>
        <label className="flex flex-col gap-1">Username
          <input className="input" autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label className="flex flex-col gap-1">Password
          <input className="input" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <ErrorText id="login-error">{error}</ErrorText>
        <button className="btn-primary" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
      </form>
    </main>
  )
}
