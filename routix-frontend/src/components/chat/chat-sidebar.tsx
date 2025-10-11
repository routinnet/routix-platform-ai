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
    <div className="h-full flex flex-col bg-white border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <Link href="/chat" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">Routix</span>
          </Link>
          
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="p-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-3 py-2">
            Recent Chats
          </h3>
          
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="px-3 py-2">
                  <div className="h-4 bg-gray-200 rounded animate-pulse mb-2" />
                  <div className="h-3 bg-gray-100 rounded animate-pulse w-2/3" />
                </div>
              ))}
            </div>
          ) : conversations.length === 0 ? (
            <div className="px-3 py-8 text-center text-gray-500">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs">Start a new chat to begin</p>
            </div>
          ) : (
            <div className="space-y-1">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => handleConversationClick(conversation.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors hover:bg-gray-100 ${
                    pathname === `/chat/${conversation.id}` ? 'bg-blue-50 border-r-2 border-blue-600' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {truncateText(conversation.title, 30)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {conversation.message_count || 0} messages
                      </p>
                    </div>
                    <span className="text-xs text-gray-400 ml-2">
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
      <div className="border-t border-gray-200 p-2">
        <nav className="space-y-1">
          <Link
            href="/chat/history"
            className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <History className="w-5 h-5" />
            <span className="text-sm">Generation History</span>
          </Link>
          
          <Link
            href="/chat/credits"
            className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <CreditCard className="w-5 h-5" />
            <span className="text-sm">Credits</span>
            <span className="ml-auto text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full">
              {user?.credits || 0}
            </span>
          </Link>
          
          <Link
            href="/chat/profile"
            className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <User className="w-5 h-5" />
            <span className="text-sm">Profile</span>
          </Link>
          
          <Link
            href="/chat/settings"
            className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Settings className="w-5 h-5" />
            <span className="text-sm">Settings</span>
          </Link>
        </nav>
      </div>

      {/* User Info */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-semibold">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.username || 'User'}
            </p>
            <p className="text-xs text-gray-500 capitalize">
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
