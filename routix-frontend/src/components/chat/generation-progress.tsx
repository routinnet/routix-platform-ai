'use client'

import { useState, useEffect } from 'react'
import { Sparkles, X, Clock, Zap } from 'lucide-react'
import { motion } from 'framer-motion'
import { Generation } from '@/types'
import { useGeneration } from '@/hooks/useGeneration'
import { generationAPI } from '@/lib/api'
import { useQueryClient } from '@tanstack/react-query'

interface GenerationProgressProps {
  generation: Generation
}

export function GenerationProgress({ generation }: GenerationProgressProps) {
  const { status } = useGeneration(generation.id)
  const [timeElapsed, setTimeElapsed] = useState(0)
  const [isCancelling, setIsCancelling] = useState(false)
  const queryClient = useQueryClient()

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
      className="glass-card rounded-3xl p-6 shadow-xl"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`status-badge w-3 h-3 rounded-full ${statusInfo.color}`} />
          <span className="text-sm font-semibold text-gray-900">
            {statusInfo.text}
          </span>
          {isActive && (
            <div className="flex items-center gap-1 text-xs text-gray-600 glass-card-dark px-3 py-1 rounded-full">
              <Clock className="w-3 h-3" />
              {formatTime(timeElapsed)}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {generation.credits_used && (
            <span className="text-xs text-gray-600 glass-card-dark px-3 py-1 rounded-full font-medium">
              {generation.credits_used} credits
            </span>
          )}
          
          {isActive && (
            <button
              onClick={async () => {
                if (isCancelling) return
                
                setIsCancelling(true)
                try {
                  await generationAPI.cancelGeneration(generation.id)
                  
                  // Invalidate queries to refresh data
                  queryClient.invalidateQueries({ queryKey: ['generation', generation.id] })
                  queryClient.invalidateQueries({ queryKey: ['generations'] })
                  
                  // Show success message (optional)
                  console.log('Generation cancelled successfully')
                } catch (error) {
                  console.error('Failed to cancel generation:', error)
                  // Show error message (optional)
                } finally {
                  setIsCancelling(false)
                }
              }}
              disabled={isCancelling}
              className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Cancel generation"
            >
              {isCancelling ? (
                <div className="w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
              ) : (
                <X className="w-4 h-4" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {isActive && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
            <span className="font-medium">{statusInfo.description}</span>
            <span className="glass-card-dark px-2 py-1 rounded-full font-bold">{progress}%</span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
            <motion.div
              className="bg-gradient-to-r from-blue-600 to-purple-600 h-2.5 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>
      )}

      {/* Generation Details */}
      <div className="space-y-3">
        <div className="flex items-start gap-3">
          <div className="glass-card-dark p-2 rounded-xl">
            <Sparkles className="w-4 h-4 text-blue-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-gray-900 font-medium line-clamp-2">
              {generation.prompt}
            </p>
            
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className="text-xs glass-card-dark px-2 py-1 rounded-full text-gray-700">
                <Zap className="w-3 h-3 inline mr-1" />
                {generation.algorithm_id}
              </span>
              
              {generation.started_at && (
                <span className="text-xs text-gray-500">
                  {new Date(generation.started_at).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {generation.status === 'failed' && generation.error_message && (
          <div className="glass-card-dark rounded-2xl p-3 border-l-4 border-red-500">
            <p className="text-sm text-red-600 font-medium">
              {generation.error_message}
            </p>
          </div>
        )}

        {/* Success Message */}
        {generation.status === 'completed' && generation.result_url && (
          <div className="glass-card-dark rounded-2xl p-3 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <p className="text-sm text-green-700 font-semibold">
                ✓ Thumbnail generated successfully!
              </p>
              <a
                href={generation.result_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-green-600 hover:text-green-700 font-medium hover-lift"
              >
                View →
              </a>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
