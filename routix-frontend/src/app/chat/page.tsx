'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowUp, Sparkles } from 'lucide-react'

export default function ChatPage() {
  const router = useRouter()
  const [input, setInput] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'ai', content: string }>>([])

  const handleStartChat = (promptText?: string) => {
    const text = promptText || input
    if (!text.trim()) return

    setMessages([{ type: 'user', content: text }])
    setInput('')
    setIsGenerating(true)

    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        type: 'ai',
        content: 'Got it ROUTIN 👋\nAnalyzing your request...\nGenerating your thumbnail preview...'
      }])
    }, 1000)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    handleStartChat()
  }

  return (
    <div className="h-full gradient-bg-main flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        {messages.length === 0 ? (
          // Initial State
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            {/* Logo */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="inline-block mb-8"
            >
              <div className="glass-card w-20 h-20 rounded-3xl flex items-center justify-center mx-auto shadow-2xl float-animation">
                <div className="text-4xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  RX
                </div>
              </div>
            </motion.div>

            {/* Main Heading */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4, ease: [0.19, 1, 0.22, 1] }}
              className="text-4xl md:text-5xl font-bold text-gray-900 mb-12 tracking-tight"
            >
              What's on your mind? ✨
            </motion.h1>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6, ease: [0.19, 1, 0.22, 1] }}
              className="grid gap-3 mb-8"
            >
              {[
                { icon: '🎨', text: 'Custom thumbnail with logo' },
                { icon: '🎮', text: 'Gaming style' },
                { icon: '💼', text: 'Professional look' },
                { icon: '📚', text: 'Tutorial style' }
              ].map((item, index) => (
                <motion.button
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ 
                    duration: 0.6, 
                    delay: 0.8 + index * 0.1,
                    ease: [0.34, 1.56, 0.64, 1]
                  }}
                  onClick={() => handleStartChat(item.text)}
                  className="glass-card p-4 rounded-2xl text-left hover:shadow-xl ultra-smooth hover-lift group"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl group-hover:scale-110 ultra-smooth">{item.icon}</span>
                    <p className="text-gray-700 font-semibold">{item.text}</p>
                  </div>
                </motion.button>
              ))}
            </motion.div>

            {/* Input Form */}
            <motion.form
              onSubmit={handleSubmit}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.2 }}
            >
              <div className="glass-card rounded-3xl p-2 shadow-2xl">
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask anything you need"
                    className="flex-1 bg-transparent border-none outline-none text-lg text-gray-800 placeholder-gray-500 px-6 py-4"
                  />
                  <button
                    type="submit"
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-2xl hover:shadow-lg transition-all hover-lift disabled:opacity-50"
                    disabled={!input.trim()}
                  >
                    <ArrowUp className="w-6 h-6" />
                  </button>
                </div>
              </div>
            </motion.form>
          </motion.div>
        ) : (
          // Chat State
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {/* Logo */}
            <div className="text-center mb-8">
              <div className="glass-card w-16 h-16 rounded-2xl inline-flex items-center justify-center shadow-xl">
                <div className="text-3xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  RX
                </div>
              </div>
            </div>

            {/* Messages */}
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.2 }}
                  className={`${message.type === 'user' ? 'flex justify-end' : 'flex justify-center'}`}
                >
                  {message.type === 'user' ? (
                    <div className="glass-card max-w-lg rounded-3xl px-6 py-4 shadow-lg">
                      <p className="text-gray-900 font-medium">{message.content}</p>
                    </div>
                  ) : (
                    <div className="glass-card max-w-2xl w-full rounded-3xl p-8 shadow-2xl">
                      <div className="text-center space-y-6">
                        <div className="text-2xl font-bold text-gray-900 mb-6">
                          ✨ Creating magic...
                        </div>
                        
                        <div className="glass-card-dark rounded-3xl p-6 space-y-4">
                          <div className="flex items-center gap-3">
                            <div className="status-badge w-2.5 h-2.5 bg-green-500 rounded-full"></div>
                            <p className="text-gray-800 font-bold">Got it! 👋</p>
                          </div>
                          <p className="text-gray-700 font-medium">🔍 Analyzing...</p>
                          <p className="text-gray-700 font-medium">🎨 Generating...</p>
                        </div>

                        <div className="flex items-center justify-center gap-3 text-gray-600 mt-4">
                          <div className="loading-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Input at bottom */}
            {!isGenerating && (
              <motion.form
                onSubmit={handleSubmit}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8"
              >
                <div className="glass-card rounded-3xl p-2 shadow-2xl">
                  <div className="flex items-center gap-3">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Continue the conversation..."
                      className="flex-1 bg-transparent border-none outline-none text-lg text-gray-800 placeholder-gray-500 px-6 py-4"
                    />
                    <button
                      type="submit"
                      className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-2xl hover:shadow-lg transition-all hover-lift disabled:opacity-50"
                      disabled={!input.trim()}
                    >
                      <ArrowUp className="w-6 h-6" />
                    </button>
                  </div>
                </div>
              </motion.form>
            )}
          </motion.div>
        )}
      </div>
    </div>
  )
}
