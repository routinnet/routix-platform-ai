'use client'

import { useState } from 'react'
import { User, Sparkles, Copy, Download, ExternalLink } from 'lucide-react'
import { Message } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false)
  
  const isUser = message.role === 'user'
  const attachments = message.attachments ? JSON.parse(message.attachments) : []

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy text:', error)
    }
  }

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Avatar */}
      {!isUser && (
        <div className="flex-shrink-0 w-10 h-10 glass-card rounded-2xl flex items-center justify-center shadow-lg">
          <Sparkles className="w-5 h-5 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent" style={{ WebkitTextFillColor: 'transparent', WebkitBackgroundClip: 'text' }} />
        </div>
      )}

      {/* Message Content */}
      <div className={`max-w-2xl ${isUser ? 'order-first' : ''}`}>
        {/* Message Bubble */}
        <div
          className={`rounded-3xl px-5 py-3.5 shadow-lg smooth-transition ${
            isUser
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white ml-auto'
              : 'glass-card text-gray-900'
          }`}
        >
          {/* Attachments */}
          {attachments.length > 0 && (
            <div className="mb-3 space-y-2">
              {attachments.map((attachment: string, index: number) => (
                <div key={index} className="relative">
                  <img
                    src={attachment}
                    alt={`Attachment ${index + 1}`}
                    className="max-w-full h-auto rounded-lg"
                    style={{ maxHeight: '200px' }}
                  />
                </div>
              ))}
            </div>
          )}

          {/* Text Content */}
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>

          {/* Generated Image Results */}
          {message.metadata && (() => {
            try {
              const metadata = JSON.parse(message.metadata)
              if (metadata.generation_result && metadata.generation_result.image_url) {
                return (
                  <div className="mt-3 space-y-3">
                    <div className="relative">
                      <img
                        src={metadata.generation_result.image_url}
                        alt="Generated thumbnail"
                        className="max-w-full h-auto rounded-lg border"
                      />
                      
                      {/* Image Actions */}
                      <div className="absolute top-2 right-2 flex gap-1">
                        <button
                          onClick={() => window.open(metadata.generation_result.image_url, '_blank')}
                          className="p-1.5 bg-black bg-opacity-50 text-white rounded-lg hover:bg-opacity-70 transition-colors"
                          title="Open in new tab"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            const link = document.createElement('a')
                            link.href = metadata.generation_result.image_url
                            link.download = 'thumbnail.jpg'
                            link.click()
                          }}
                          className="p-1.5 bg-black bg-opacity-50 text-white rounded-lg hover:bg-opacity-70 transition-colors"
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {/* Generation Info */}
                    <div className={`text-xs ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
                      <div className="flex items-center justify-between">
                        <span>
                          Generated with {metadata.generation_result.algorithm || 'AI'}
                        </span>
                        {metadata.generation_result.processing_time && (
                          <span>
                            {metadata.generation_result.processing_time}s
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              }
            } catch (error) {
              return null
            }
          })()}
        </div>

        {/* Message Footer */}
        <div className={`flex items-center gap-2 mt-1 text-xs text-gray-500 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span>{formatRelativeTime(message.created_at)}</span>
          
          {!isUser && (
            <button
              onClick={handleCopy}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              title="Copy message"
            >
              <Copy className="w-3 h-3" />
            </button>
          )}
          
          {copied && (
            <span className="text-green-600 font-medium">Copied!</span>
          )}
        </div>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="flex-shrink-0 w-10 h-10 glass-card rounded-2xl flex items-center justify-center shadow-lg">
          <User className="w-5 h-5 text-gray-700" />
        </div>
      )}
    </div>
  )
}
