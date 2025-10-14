'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Eye, EyeOff, Loader2, Check, X } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const { register, isRegistering, registerError } = useAuth()
  const router = useRouter()

  // Password validation
  const passwordRequirements = [
    { label: 'At least 6 characters', test: (pwd: string) => pwd.length >= 6 },
    { label: 'Contains uppercase letter', test: (pwd: string) => /[A-Z]/.test(pwd) },
    { label: 'Contains lowercase letter', test: (pwd: string) => /[a-z]/.test(pwd) },
    { label: 'Contains number', test: (pwd: string) => /\d/.test(pwd) },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    // Validation
    const newErrors: Record<string, string> = {}
    
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email'
    }

    if (!formData.username) {
      newErrors.username = 'Username is required'
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password
      })
      router.push('/chat')
    } catch (error: any) {
      console.error('Registration error:', error)
    }
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
          Create Your Account ✨
        </h1>
        <p className="text-gray-600">
          Join thousands of creators using AI to make stunning thumbnails
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
            <p className="mt-1 text-sm text-red-600">{errors.email}</p>
          )}
        </div>

        {/* Username */}
        <div>
          <label htmlFor="username" className="block text-sm font-semibold text-gray-700 mb-2">
            Username
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className={`glass-input w-full px-5 py-3.5 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all ${
              errors.username ? 'border-red-500' : ''
            }`}
            placeholder="Choose a username"
          />
          {errors.username && (
            <p className="mt-1 text-sm text-red-600">{errors.username}</p>
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
              placeholder="Create a password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1 rounded-lg hover:bg-gray-100/50 transition-colors"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          
          {/* Password Requirements */}
          {formData.password && (
            <div className="mt-3 glass-card-dark rounded-2xl p-3 space-y-2">
              {passwordRequirements.map((req, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  {req.test(formData.password) ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <X className="w-4 h-4 text-gray-400" />
                  )}
                  <span className={req.test(formData.password) ? 'text-green-700 font-medium' : 'text-gray-600'}>
                    {req.label}
                  </span>
                </div>
              ))}
            </div>
          )}
          
          {errors.password && (
            <p className="mt-1 text-sm text-red-600">{errors.password}</p>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-semibold text-gray-700 mb-2">
            Confirm Password
          </label>
          <div className="relative">
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className={`glass-input w-full px-5 py-3.5 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all pr-14 ${
                errors.confirmPassword ? 'border-red-500' : ''
              }`}
              placeholder="Confirm your password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1 rounded-lg hover:bg-gray-100/50 transition-colors"
            >
              {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.confirmPassword && (
            <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
          )}
        </div>

        {/* Registration Error */}
        {registerError && (
          <div className="glass-card-dark border-l-4 border-red-500 rounded-2xl p-4">
            <p className="text-sm text-red-600 font-medium">
              {registerError.response?.data?.detail || 'Registration failed. Please try again.'}
            </p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isRegistering}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-2xl font-bold text-lg hover:shadow-xl focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 hover-lift"
        >
          {isRegistering ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Creating Account...
            </>
          ) : (
            'Create Account'
          )}
        </button>

        {/* Terms */}
        <p className="text-xs text-gray-600 text-center">
          By creating an account, you agree to our{' '}
          <Link href="/terms" className="text-blue-600 hover:text-blue-700">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link href="/privacy" className="text-blue-600 hover:text-blue-700">
            Privacy Policy
          </Link>
        </p>
      </form>

      {/* Sign In Link */}
      <div className="mt-8 text-center">
        <p className="text-gray-700">
          Already have an account?{' '}
          <Link 
            href="/auth/login" 
            className="text-blue-600 hover:text-blue-700 font-bold transition-colors"
          >
            Sign in →
          </Link>
        </p>
      </div>
    </div>
  )
}
