'use client'

import { useState, useEffect } from 'react'
import { Sparkles, X, Clock, Zap } from 'lucide-react'
import { motion } from 'framer-motion'
import { Generation } from '@/types'
import { useGeneration } from '@/hooks/useGeneration'

interface GenerationProgressProps {
  generation: Generation
}

export function GenerationProgress({ generation }: GenerationProgressProps) {
  const { status } = useGeneration(generation.id)
  const [timeElapsed, setTimeElapsed] = useState(0)

  // Track elapsed time
  useEffect(() => {
    if (generation.status === 'processing' || generation.status === 'queued') {
      const startTime = new Date(generation.started_at || generation.created_at).getTime()
      
      const interval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000)
        setTimeElapsed(elapsed)
      }, 1000)

      return () => clearInterval(interval)
    }
  }, [generation.status, generation.started_at, generation.created_at])

  const getStatusInfo = () => {
    switch (generation.status) {
      case 'queued':
        return {
          color: 'bg-yellow-500',
          text: 'Queued',
          description: 'Waiting in queue...'
        }
      case 'processing':
        return {
          color: 'bg-blue-500',
          text: 'Generating',
          description: 'AI is creating your thumbnail...'
        }
      case 'completed':
        return {
          color: 'bg-green-500',
          text: 'Completed',
          description: 'Thumbnail generated successfully!'
        }
      case 'failed':
        return {
          color: 'bg-red-500',
          text: 'Failed',
          description: generation.error_message || 'Generation failed'
        }
      case 'cancelled':
        return {
          color: 'bg-gray-500',
          text: 'Cancelled',
          description: 'Generation was cancelled'
        }
      default:
        return {
          color: 'bg-gray-500',
          text: 'Unknown',
          description: 'Unknown status'
        }
    }
  }

  const statusInfo = getStatusInfo()
  const progress = status?.progress || generation.progress || 0
  const isActive = generation.status === 'queued' || generation.status === 'processing'

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="bg-white border border-gray-200 rounded-xl p-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${statusInfo.color} ${isActive ? 'animate-pulse' : ''}`} />
          <span className="text-sm font-medium text-gray-900">
            {statusInfo.text}
          </span>
          {isActive && (
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <Clock className="w-3 h-3" />
              {formatTime(timeElapsed)}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {generation.credits_used && (
            <span className="text-xs text-gray-500">
              {generation.credits_used} credits
            </span>
          )}
          
          {isActive && (
            <button
              onClick={() => {
                // TODO: Implement cancel generation
                console.log('Cancel generation:', generation.id)
              }}
              className="p-1 text-gray-400 hover:text-red-500 transition-colors"
              title="Cancel generation"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {isActive && (
        <div className="mb-3">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span>{statusInfo.description}</span>
            <span>{progress}%</span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-blue-500 h-2 rounded-full progress-bar"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      )}

      {/* Generation Details */}
      <div className="space-y-2">
        <div className="flex items-start gap-2">
          <Sparkles className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm text-gray-900 truncate">
              {generation.prompt}
            </p>
            
            <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
              <span>Algorithm: {generation.algorithm_id}</span>
              
              {generation.started_at && (
                <span>
                  Started: {new Date(generation.started_at).toLocaleTimeString()}
                </span>
              )}
              
              {generation.completed_at && (
                <span>
                  Completed: {new Date(generation.completed_at).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {generation.status === 'failed' && generation.error_message && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-2">
            <p className="text-sm text-red-600">
              {generation.error_message}
            </p>
          </div>
        )}

        {/* Success Message */}
        {generation.status === 'completed' && generation.result_url && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-2">
            <div className="flex items-center justify-between">
              <p className="text-sm text-green-600">
                Thumbnail generated successfully!
              </p>
              <a
                href={generation.result_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-green-600 hover:text-green-700 underline"
              >
                View Result
              </a>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
