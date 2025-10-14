'use client'

import { Menu, LogOut, User, Settings } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useAuthStore, useUIStore } from '@/lib/store'
import { useState } from 'react'

export function ChatHeader() {
  const { user } = useAuthStore()
  const { sidebarOpen, setSidebarOpen } = useUIStore()
  const { logout } = useAuth()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = () => {
    logout()
    setShowUserMenu(false)
  }

  return (
    <header className="glass-card border-b border-white/30 px-4 py-3 shadow-sm">
      <div className="flex items-center justify-between">
        {/* Left Side */}
        <div className="flex items-center gap-4">
          {/* Mobile Menu Button */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-white/50 rounded-2xl transition-all hover-lift"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Title */}
          <div>
            <h1 className="text-lg font-bold text-gray-900">
              AI Thumbnail Generator ✨
            </h1>
            <p className="text-sm text-gray-600 font-medium">
              Create stunning thumbnails with AI
            </p>
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-4">
          {/* Credits Display */}
          <div className="hidden sm:flex items-center gap-2 glass-card-dark px-4 py-2 rounded-full shadow-md">
            <span className="text-sm font-bold text-blue-600">
              {user?.credits || 0} credits
            </span>
          </div>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 p-2 hover:bg-white/50 rounded-2xl transition-all hover-lift"
            >
              <div className="w-9 h-9 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-md">
                <span className="text-white text-sm font-bold">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <span className="hidden sm:block text-sm font-bold text-gray-800">
                {user?.username || 'User'}
              </span>
            </button>

            {/* Dropdown Menu */}
            {showUserMenu && (
              <div className="absolute right-0 top-full mt-2 w-52 glass-card rounded-3xl shadow-2xl z-50 border border-white/40">
                <div className="p-2">
                  <div className="px-3 py-3 border-b border-white/30">
                    <p className="text-sm font-bold text-gray-900">
                      {user?.username || 'User'}
                    </p>
                    <p className="text-xs text-gray-600 mt-0.5">
                      {user?.email}
                    </p>
                    <p className="text-xs text-blue-600 capitalize font-semibold mt-1">
                      {user?.subscription_tier || 'free'} plan
                    </p>
                  </div>

                  <div className="py-1">
                    <button
                      onClick={() => setShowUserMenu(false)}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-gray-700 hover:bg-white/50 rounded-2xl transition-all font-medium"
                    >
                      <div className="glass-card-dark p-1 rounded-lg">
                        <User className="w-4 h-4" />
                      </div>
                      Profile
                    </button>
                    
                    <button
                      onClick={() => setShowUserMenu(false)}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-gray-700 hover:bg-white/50 rounded-2xl transition-all font-medium"
                    >
                      <div className="glass-card-dark p-1 rounded-lg">
                        <Settings className="w-4 h-4" />
                      </div>
                      Settings
                    </button>
                  </div>

                  <div className="border-t border-white/30 pt-1">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-red-600 hover:bg-red-50 rounded-2xl transition-all font-bold"
                    >
                      <div className="glass-card-dark p-1 rounded-lg">
                        <LogOut className="w-4 h-4" />
                      </div>
                      Sign Out
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Click outside to close menu */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </header>
  )
}
