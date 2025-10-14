'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { 
  Plus, 
  MessageSquare, 
  Sparkles, 
  Settings, 
  User, 
  CreditCard,
  History,
  Menu,
  X
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useConversations } from '@/hooks/useChat'
import { useAuthStore, useUIStore } from '@/lib/store'
import { formatRelativeTime, truncateText } from '@/lib/utils'

export function ChatSidebar() {
  const { conversations, createConversation, deleteConversation, isLoading } = useConversations()
  const { user } = useAuthStore()
  const { sidebarOpen, setSidebarOpen } = useUIStore()
  const router = useRouter()
  const pathname = usePathname()

  const handleNewChat = () => {
    createConversation({ title: 'New Conversation' })
  }

  const handleConversationClick = (conversationId: string) => {
    router.push(`/chat/${conversationId}`)
    // Close sidebar on mobile
    if (window.innerWidth < 768) {
      setSidebarOpen(false)
    }
  }

  const sidebarContent = (
    <div className="h-full flex flex-col glass-card border-r border-white/30">
      {/* Header */}
      <div className="p-4 border-b border-white/30">
        <div className="flex items-center justify-between mb-4">
          <Link href="/chat" className="flex items-center space-x-2 hover-lift smooth-transition">
            <div className="glass-card-dark w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg">
              <div className="text-2xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                RX
              </div>
            </div>
            <span className="text-xl font-bold text-gray-900">Routix</span>
          </Link>
          
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden p-2 hover:bg-white/50 rounded-xl transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-3 px-4 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:shadow-xl transition-all font-semibold hover-lift"
        >
          <Plus className="w-5 h-5" />
          New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="p-3">
          <h3 className="text-xs font-bold text-gray-600 uppercase tracking-wider px-3 py-2">
            Recent Chats
          </h3>
          
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="glass-card-dark rounded-2xl p-3 animate-pulse">
                  <div className="h-4 bg-white/30 rounded mb-2" />
                  <div className="h-3 bg-white/20 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : conversations.length === 0 ? (
            <div className="px-3 py-8 text-center">
              <div className="glass-card-dark w-16 h-16 rounded-3xl flex items-center justify-center mx-auto mb-3">
                <MessageSquare className="w-8 h-8 text-gray-500" />
              </div>
              <p className="text-sm font-medium text-gray-700">No conversations yet</p>
              <p className="text-xs text-gray-500 mt-1">Start a new chat to begin</p>
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => handleConversationClick(conversation.id)}
                  className={`w-full text-left px-3 py-3 rounded-2xl transition-all smooth-transition hover-lift ${
                    pathname === `/chat/${conversation.id}` 
                      ? 'glass-card-dark border-l-4 border-blue-600 shadow-lg' 
                      : 'hover:bg-white/30'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-900 truncate">
                        {truncateText(conversation.title, 28)}
                      </p>
                      <p className="text-xs text-gray-600 mt-0.5">
                        {conversation.message_count || 0} messages
                      </p>
                    </div>
                    <span className="text-xs text-gray-500 mt-0.5 shrink-0">
                      {formatRelativeTime(conversation.updated_at)}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Navigation Menu */}
      <div className="border-t border-white/30 p-3">
        <nav className="space-y-1">
          <Link
            href="/chat/history"
            className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-white/40 rounded-2xl transition-all font-medium smooth-transition hover-lift"
          >
            <div className="glass-card-dark p-1.5 rounded-lg">
              <History className="w-4 h-4" />
            </div>
            <span className="text-sm">History</span>
          </Link>
          
          <Link
            href="/chat/credits"
            className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-white/40 rounded-2xl transition-all font-medium smooth-transition hover-lift"
          >
            <div className="glass-card-dark p-1.5 rounded-lg">
              <CreditCard className="w-4 h-4" />
            </div>
            <span className="text-sm">Credits</span>
            <span className="ml-auto text-xs glass-card-dark px-2 py-1 rounded-full font-bold text-blue-600">
              {user?.credits || 0}
            </span>
          </Link>
          
          <Link
            href="/chat/profile"
            className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-white/40 rounded-2xl transition-all font-medium smooth-transition hover-lift"
          >
            <div className="glass-card-dark p-1.5 rounded-lg">
              <User className="w-4 h-4" />
            </div>
            <span className="text-sm">Profile</span>
          </Link>
          
          <Link
            href="/chat/settings"
            className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-white/40 rounded-2xl transition-all font-medium smooth-transition hover-lift"
          >
            <div className="glass-card-dark p-1.5 rounded-lg">
              <Settings className="w-4 h-4" />
            </div>
            <span className="text-sm">Settings</span>
          </Link>
        </nav>
      </div>

      {/* User Info */}
      <div className="border-t border-white/30 p-4">
        <div className="glass-card-dark rounded-2xl p-3 flex items-center gap-3 shadow-lg">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-md">
            <span className="text-white text-sm font-bold">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-gray-900 truncate">
              {user?.username || 'User'}
            </p>
            <p className="text-xs text-gray-600 capitalize font-medium">
              {user?.subscription_tier || 'free'} plan
            </p>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <div className={`hidden md:block w-80 transition-all duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        {sidebarContent}
      </div>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
              className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
            />
            
            {/* Sidebar */}
            <motion.div
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="md:hidden fixed left-0 top-0 w-80 h-full z-50"
            >
              {sidebarContent}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
