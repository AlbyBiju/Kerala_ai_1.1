import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/shipments', label: 'Shipments' },
]

export default function AppLayout() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-64 flex-col justify-between bg-slate-900 p-6 text-slate-100">
        <div>
          <div className="mb-8">
            <h1 className="text-xl font-bold tracking-tight">ExportGuard</h1>
            <p className="mt-1 text-xs text-slate-400">Verify Before You Ship</p>
          </div>
          <nav className="flex flex-col gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium transition ${
                    isActive ? 'bg-slate-700 text-white' : 'text-slate-300 hover:bg-slate-800'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <button
          onClick={handleLogout}
          className="rounded-lg px-3 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white"
        >
          Log out
        </button>
      </aside>
      <main className="flex-1 p-8">
        <Outlet />
      </main>
    </div>
  )
}
