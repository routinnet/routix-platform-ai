export interface User {
  id: string
  email: string
  username: string
  credits: number
  subscription_tier: 'free' | 'pro' | 'enterprise'
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
  total_generations?: number
  successful_generations?: number
  total_credits_used?: number
}

export interface Conversation {
  id: string
  user_id: string
  title: string
  is_archived: boolean
  created_at: string
  updated_at: string
  message_count?: number
  last_message_at?: string
  messages?: Message[]
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  attachments?: string
  metadata?: string
  created_at: string
}

export interface Generation {
  id: string
  user_id: string
  conversation_id?: string
  algorithm_id: string
  prompt: string
  reference_images?: string[]
  parameters?: Record<string, any>
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  error_message?: string
  result_url?: string
  result_metadata?: Record<string, any>
  credits_used: number
  created_at: string
  started_at?: string
  completed_at?: string
  duration_seconds?: number
}

export interface Algorithm {
  id: string
  name: string
  display_name: string
  description: string
  cost_credits: number
  is_active: boolean
  parameters?: Record<string, any>
}

export interface CreditTransaction {
  id: string
  user_id: string
  type: string
  amount: number
  description: string
  reference_id?: string
  created_at: string
}

export interface GenerationProgress {
  generation_id: string
  status: Generation['status']
  progress: number
  message?: string
  estimated_completion?: string
}

export interface GenerationStats {
  total_generations: number
  successful_generations: number
  failed_generations: number
  total_credits_used: number
  average_completion_time?: number
  most_used_algorithm?: string
}

export interface ChatRequest {
  message: string
  attachments?: string[]
  metadata?: Record<string, any>
}

export interface ChatResponse {
  message: Message
  conversation_id: string
  requires_generation: boolean
  generation_id?: string
}

export interface FileUpload {
  filename: string
  original_filename: string
  file_path: string
  file_url: string
  file_size: number
  content_type: string
}

export interface PaginatedResponse<T> {
  items?: T[]
  conversations?: T[]
  generations?: T[]
  transactions?: T[]
  total: number
  page: number
  per_page: number
  has_next: boolean
  has_prev: boolean
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}
