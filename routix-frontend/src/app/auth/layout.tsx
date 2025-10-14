'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen animated-gradient flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <Link href="/" className="inline-block">
            <div className="glass-card w-16 h-16 rounded-3xl flex items-center justify-center mx-auto shadow-2xl hover-lift smooth-transition">
              <div className="text-3xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                RX
              </div>
            </div>
          </Link>
        </motion.div>

        {/* Auth Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="glass-card rounded-3xl shadow-2xl p-8"
        >
          {children}
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-6"
        >
          <Link 
            href="/" 
            className="glass-card-dark px-6 py-3 rounded-full inline-flex items-center gap-2 text-gray-700 hover:text-gray-900 font-medium smooth-transition hover-lift"
          >
            ← Back to home
          </Link>
        </motion.div>
      </div>
    </div>
  )
}
