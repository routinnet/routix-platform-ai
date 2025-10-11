'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, Image, Loader2, Sparkles } from 'lucide-react'
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
    <div className="h-full flex flex-col bg-gray-50">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Start Creating Amazing Thumbnails
              </h3>
              <p className="text-gray-600 mb-6">
                Describe the thumbnail you want to create, upload reference images, 
                and let our AI generate stunning results for you.
              </p>
              <div className="text-sm text-gray-500">
                <p>Try saying something like:</p>
                <p className="italic mt-1">
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
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <ChatMessage message={msg} />
              </motion.div>
            ))}
          </AnimatePresence>
        )}

        {/* Active Generations */}
        {activeGenerations.length > 0 && (
          <div className="space-y-4">
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
            className="flex items-center gap-2 text-gray-500"
          >
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className="text-sm">AI is thinking...</span>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4">
        {/* Attachments Preview */}
        {attachments.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {attachments.map((attachment, index) => (
                <div
                  key={index}
                  className="relative bg-gray-100 rounded-lg p-2 flex items-center gap-2"
                >
                  <Image className="w-4 h-4 text-gray-600" />
                  <span className="text-sm text-gray-700 truncate max-w-32">
                    {attachment.split('/').pop()}
                  </span>
                  <button
                    onClick={() => removeAttachment(index)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex items-end gap-3">
          {/* File Upload Button */}
          <button
            type="button"
            onClick={() => setShowFileUpload(true)}
            className="flex-shrink-0 p-3 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
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
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none max-h-32 scrollbar-thin"
              rows={1}
              disabled={isSending}
            />
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={(!message.trim() && attachments.length === 0) || isSending}
            className="flex-shrink-0 p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSending ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>

        {/* Helper Text */}
        <div className="mt-2 text-xs text-gray-500 text-center">
          Press Enter to send, Shift+Enter for new line
        </div>
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
