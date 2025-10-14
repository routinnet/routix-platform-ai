'use client'

import { useState, useRef, useEffect } from 'react'
import { ArrowUp, Paperclip, Image, Loader2, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useConversation } from '@/hooks/useChat'
import { useGenerations } from '@/hooks/useGeneration'
import { ChatMessage } from './chat-message'
import { FileUpload } from './file-upload'
import { GenerationProgress } from './generation-progress'

interface ChatInterfaceProps {
  conversationId: string
}

export function ChatInterface({ conversationId }: ChatInterfaceProps) {
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<string[]>([])
  const [showFileUpload, setShowFileUpload] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const { conversation, messages, chat, isSending } = useConversation(conversationId)
  const { activeGenerations } = useGenerations()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim() && attachments.length === 0) return
    
    const messageData = {
      message: message.trim(),
      attachments: attachments.length > 0 ? attachments : undefined
    }

    try {
      await chat({ conversationId, data: messageData })
      setMessage('')
      setAttachments([])
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleFileUpload = (files: string[]) => {
    setAttachments(prev => [...prev, ...files])
    setShowFileUpload(false)
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="h-full flex flex-col gradient-bg-main">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="glass-card w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl float-animation">
                <div className="text-4xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  RX
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Start Creating Amazing Thumbnails
              </h3>
              <p className="text-gray-700 mb-6">
                Describe the thumbnail you want to create, upload reference images, 
                and let our AI generate stunning results for you.
              </p>
              <div className="glass-card rounded-2xl p-4 text-sm text-gray-700">
                <p className="font-semibold mb-1">Try saying something like:</p>
                <p className="italic">
                  "Create a gaming thumbnail for my Fortnite video with bright colors and action scene"
                </p>
              </div>
            </div>
          </div>
        ) : (
          <AnimatePresence>
            {messages.map((msg, index) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
              >
                <ChatMessage message={msg} />
              </motion.div>
            ))}
          </AnimatePresence>
        )}

        {/* Active Generations */}
        {activeGenerations.length > 0 && (
          <div className="space-y-6">
            {activeGenerations.map((generation) => (
              <GenerationProgress key={generation.id} generation={generation} />
            ))}
          </div>
        )}

        {/* Typing Indicator */}
        {isSending && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-3"
          >
            <div className="glass-card w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg">
              <Sparkles className="w-5 h-5 text-blue-600" />
            </div>
            <div className="glass-card px-4 py-2 rounded-2xl flex items-center gap-2">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="text-sm text-gray-700 font-medium">AI is thinking...</span>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="glass-card mx-6 mb-6 rounded-3xl p-2 shadow-2xl">
        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          {/* File Upload Button */}
          <button
            type="button"
            onClick={() => setShowFileUpload(true)}
            className="flex-shrink-0 p-3 text-gray-600 hover:bg-gray-100/50 rounded-xl transition-all hover-lift"
            title="Upload file"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          {/* Message Input */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe the thumbnail you want to create..."
              className="w-full bg-transparent border-none outline-none text-lg text-gray-800 placeholder-gray-500 px-2 py-3 resize-none max-h-32 scrollbar-thin"
              rows={1}
              disabled={isSending}
            />
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={(!message.trim() && attachments.length === 0) || isSending}
            className="flex-shrink-0 p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:shadow-lg transition-all hover-lift disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSending ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : (
              <ArrowUp className="w-6 h-6" />
            )}
          </button>
        </form>

        {/* Attachments Preview */}
        {attachments.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {attachments.map((attachment, index) => (
              <div
                key={index}
                className="glass-card-dark rounded-xl p-2 flex items-center gap-2"
              >
                <Image className="w-4 h-4 text-gray-600" />
                <span className="text-sm text-gray-700 truncate max-w-32">
                  {attachment.split('/').pop()}
                </span>
                <button
                  onClick={() => removeAttachment(index)}
                  className="text-gray-500 hover:text-red-500 transition-colors"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* File Upload Modal */}
      {showFileUpload && (
        <FileUpload
          onUpload={handleFileUpload}
          onClose={() => setShowFileUpload(false)}
        />
      )}
    </div>
  )
}
