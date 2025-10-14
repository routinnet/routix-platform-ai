'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Sparkles, Zap, Image, MessageSquare } from 'lucide-react'
import { useConversations } from '@/hooks/useChat'
import { motion } from 'framer-motion'

export default function ChatPage() {
  const router = useRouter()
  const { createConversation, isCreating } = useConversations()

  const handleStartNewChat = () => {
    createConversation(
      { title: 'New Conversation' },
      {
        onSuccess: (response) => {
          if (response?.data?.id) {
            router.push(`/chat/${response.data.id}`)
          }
        },
        onError: (error) => {
          console.error('Failed to create conversation:', error)
        }
      }
    )
  }

  const examples = [
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "Gaming Thumbnail",
      description: "Create an epic gaming thumbnail with neon effects and action elements",
      prompt: "Create a gaming thumbnail for my Fortnite video with bright colors, action scene, and victory theme"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Tech Review",
      description: "Professional tech thumbnail with product showcase and clean design",
      prompt: "Make a tech review thumbnail for iPhone 15 Pro with sleek design and professional look"
    },
    {
      icon: <Image className="w-6 h-6" />,
      title: "Tutorial Video",
      description: "Educational thumbnail with clear text and instructional elements",
      prompt: "Design a tutorial thumbnail for 'How to Code in Python' with educational style and clear text"
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "Vlog Style",
      description: "Personal vlog thumbnail with expressive design and lifestyle elements",
      prompt: "Create a vlog thumbnail for 'My Morning Routine' with lifestyle aesthetic and personal touch"
    }
  ]

  return (
    <div className="h-full flex items-center justify-center p-8">
      <div className="max-w-4xl w-full">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to Routix
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Create stunning AI-powered thumbnails for your content. 
            Simply describe what you want, and our AI will generate professional designs in seconds.
          </p>

          <button
            onClick={handleStartNewChat}
            disabled={isCreating}
            className="bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto hover-lift"
          >
            <MessageSquare className="w-6 h-6" />
            {isCreating ? 'Starting...' : 'Start New Chat'}
          </button>
        </motion.div>

        {/* Example Prompts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Try These Examples
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            {examples.map((example, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                onClick={handleStartNewChat}
                className="text-left p-6 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all hover-lift"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 flex-shrink-0">
                    {example.icon}
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {example.title}
                    </h3>
                    <p className="text-gray-600 mb-3">
                      {example.description}
                    </p>
                    <p className="text-sm text-blue-600 font-medium">
                      "{example.prompt}"
                    </p>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 text-center"
        >
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Zap className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Lightning Fast
              </h3>
              <p className="text-gray-600">
                Generate professional thumbnails in seconds with our optimized AI pipeline.
              </p>
            </div>

            <div className="p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI-Powered
              </h3>
              <p className="text-gray-600">
                Advanced AI algorithms including DALL-E, Midjourney, and Stable Diffusion.
              </p>
            </div>

            <div className="p-6">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Chat Interface
              </h3>
              <p className="text-gray-600">
                Describe your vision naturally. No design skills required.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
