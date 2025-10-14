'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowUp } from 'lucide-react'

export function LandingPage() {
  const [input, setInput] = useState('')
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      // Navigate to register or chat
      router.push('/auth/register')
    }
  }

  return (
    <div className="min-h-screen animated-gradient flex items-center justify-center p-6">
      <div className="w-full max-w-3xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
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
            className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight"
          >
            Hey Armando! 👋
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6, ease: [0.19, 1, 0.22, 1] }}
            className="text-xl md:text-2xl text-white/70 mb-12 font-light"
          >
            What can I create for you?
          </motion.p>

          {/* Input Section */}
          <motion.form
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="relative"
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

          {/* Helper Text */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1.2, ease: [0.19, 1, 0.22, 1] }}
            className="mt-6 text-white/60 text-sm font-light"
          >
            <p>💡 Try: "Gaming thumbnail with neon effects"</p>
          </motion.div>
        </motion.div>

        {/* Features Pills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.4, ease: [0.19, 1, 0.22, 1] }}
          className="flex flex-wrap justify-center gap-3"
        >
          {['✨ AI-Powered', '⚡ Fast', '🎨 No Skills Needed'].map((feature, index) => (
            <motion.div
              key={feature}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ 
                duration: 0.6, 
                delay: 1.6 + index * 0.15,
                ease: [0.34, 1.56, 0.64, 1]
              }}
              className="glass-card px-5 py-2.5 rounded-full text-white/90 font-medium text-sm shadow-lg hover-lift ultra-smooth backdrop-blur-xl"
            >
              {feature}
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  )
}
