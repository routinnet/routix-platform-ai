'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { X, Upload, Image, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { fileAPI } from '@/lib/api'
import { formatFileSize } from '@/lib/utils'

interface FileUploadProps {
  onUpload: (files: string[]) => void
  onClose: () => void
}

export function FileUpload({ onUpload, onClose }: FileUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true)
    setError(null)
    
    try {
      const uploadPromises = acceptedFiles.map(file => fileAPI.upload(file))
      const responses = await Promise.all(uploadPromises)
      
      const fileUrls = responses.map(response => response.data.file_url)
      setUploadedFiles(prev => [...prev, ...fileUrls])
      
    } catch (error: any) {
      console.error('Upload error:', error)
      setError(error.response?.data?.detail || 'Failed to upload files')
    } finally {
      setUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp', '.gif']
    },
    maxFiles: 5,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  const handleConfirm = () => {
    if (uploadedFiles.length > 0) {
      onUpload(uploadedFiles)
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-2xl p-6 w-full max-w-md"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Upload Reference Images
          </h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          
          <div className="space-y-4">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto">
              <Upload className="w-6 h-6 text-gray-600" />
            </div>
            
            {isDragActive ? (
              <p className="text-blue-600 font-medium">
                Drop the files here...
              </p>
            ) : (
              <div>
                <p className="text-gray-900 font-medium mb-1">
                  Click to upload or drag and drop
                </p>
                <p className="text-sm text-gray-500">
                  PNG, JPG, WEBP up to 10MB each
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Uploaded Files */}
        {uploadedFiles.length > 0 && (
          <div className="mt-6 space-y-3">
            <h4 className="text-sm font-medium text-gray-900">
              Uploaded Files ({uploadedFiles.length})
            </h4>
            
            <div className="space-y-2 max-h-40 overflow-y-auto scrollbar-thin">
              {uploadedFiles.map((fileUrl, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg"
                >
                  <div className="w-10 h-10 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                    <img
                      src={fileUrl}
                      alt={`Upload ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      Image {index + 1}
                    </p>
                    <p className="text-xs text-gray-500">
                      Reference image
                    </p>
                  </div>
                  
                  <button
                    onClick={() => removeFile(index)}
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Loading State */}
        {uploading && (
          <div className="mt-4 flex items-center justify-center gap-2 text-blue-600">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Uploading files...</span>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          
          <button
            onClick={handleConfirm}
            disabled={uploadedFiles.length === 0 || uploading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Add Files ({uploadedFiles.length})
          </button>
        </div>
      </motion.div>
    </div>
  )
}
