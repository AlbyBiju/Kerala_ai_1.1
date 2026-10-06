import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

interface LoginForm {
  username: string
  password: string
}

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>()

  const onSubmit = async (values: LoginForm) => {
    setSubmitting(true)
    try {
      await login(values.username, values.password)
      toast.success('Welcome back!')
      navigate('/dashboard')
    } catch {
      toast.error('Invalid credentials')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl">
        <h1 className="text-2xl font-bold text-slate-900">ExportGuard</h1>
        <p className="mt-1 text-sm text-slate-500">Sign in with your team credentials</p>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-700">
              Username
            </label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              {...register('username', { required: 'Username is required' })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            />
            {errors.username && (
              <p className="mt-1 text-xs text-red-600">{errors.username.message}</p>
            )}
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              {...register('password', { required: 'Password is required' })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            />
            {errors.password && (
              <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
            )}
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-slate-900 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
