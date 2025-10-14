'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

export default function LoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const { login, isLoggingIn, loginError } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    // Basic validation
    const newErrors: Record<string, string> = {}
    if (!formData.email) newErrors.email = 'Email is required'
    if (!formData.password) newErrors.password = 'Password is required'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    login(formData, {
      onSuccess: () => {
        router.push('/chat')
      },
      onError: (error: any) => {
        console.error('Login error:', error)
      }
    })
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  return (
    <div>
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Welcome Back! 👋
        </h1>
        <p className="text-gray-600">
          Sign in to continue creating amazing thumbnails
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
            Email Address
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`glass-input w-full px-5 py-3.5 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all ${
              errors.email ? 'border-red-500' : ''
            }`}
            placeholder="you@example.com"
          />
          {errors.email && (
            <p className="mt-2 text-sm text-red-600 font-medium">{errors.email}</p>
          )}
        </div>

        {/* Password */}
        <div>
          <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
            Password
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`glass-input w-full px-5 py-3.5 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all pr-14 ${
                errors.password ? 'border-red-500' : ''
              }`}
              placeholder="••••••••"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1 rounded-lg hover:bg-gray-100/50 transition-colors"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.password && (
            <p className="mt-2 text-sm text-red-600 font-medium">{errors.password}</p>
          )}
        </div>

        {/* Login Error */}
        {loginError && (
          <div className="glass-card-dark border-l-4 border-red-500 rounded-2xl p-4">
            <p className="text-sm text-red-600 font-medium">
              {loginError.response?.data?.detail || 'Login failed. Please try again.'}
            </p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoggingIn}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-2xl font-bold text-lg hover:shadow-xl focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 hover-lift"
        >
          {isLoggingIn ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Signing In...
            </>
          ) : (
            'Sign In'
          )}
        </button>

        {/* Forgot Password */}
        <div className="text-center">
          <Link 
            href="/auth/forgot-password" 
            className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors inline-flex items-center gap-1"
          >
            Forgot your password? →
          </Link>
        </div>
      </form>

      {/* Sign Up Link */}
      <div className="mt-8 text-center">
        <p className="text-gray-700">
          Don't have an account?{' '}
          <Link 
            href="/auth/register" 
            className="text-blue-600 hover:text-blue-700 font-bold transition-colors"
          >
            Sign up for free →
          </Link>
        </p>
      </div>
    </div>
  )
}
