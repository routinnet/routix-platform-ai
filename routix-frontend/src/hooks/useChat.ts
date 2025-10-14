import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useChatStore } from '@/lib/store'
import { chatAPI } from '@/lib/api'
import { Conversation, Message, ChatRequest } from '@/types'

export function useConversations() {
  const { conversations, setConversations, addConversation, updateConversation, removeConversation } = useChatStore()
  const queryClient = useQueryClient()

  const conversationsQuery = useQuery({
    queryKey: ['conversations'],
    queryFn: () => chatAPI.getConversations().then(res => res.data.conversations),
  })

  const createConversationMutation = useMutation({
    mutationFn: chatAPI.createConversation,
    onSuccess: (data) => {
      const newConversation = data.data
      addConversation(newConversation)
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  const deleteConversationMutation = useMutation({
    mutationFn: chatAPI.deleteConversation,
    onSuccess: (_, conversationId) => {
      removeConversation(conversationId)
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  return {
    conversations,
    isLoading: conversationsQuery.isLoading,
    error: conversationsQuery.error,
    createConversation: createConversationMutation.mutate,
    deleteConversation: deleteConversationMutation.mutate,
    isCreating: createConversationMutation.isPending,
    isDeleting: deleteConversationMutation.isPending,
    refetch: conversationsQuery.refetch,
  }
}

export function useConversation(conversationId: string | null) {
  const { currentConversation, setCurrentConversation } = useChatStore()
  const queryClient = useQueryClient()
  const [messages, setMessages] = useState<Message[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStatus, setProcessingStatus] = useState<string>('')

  // دریافت token از localStorage یا store
  const getToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token')
    }
    return null
  }

  const conversationQuery = useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => conversationId ? chatAPI.getConversation(conversationId).then(res => res.data) : null,
    enabled: !!conversationId,
  })

  // بارگذاری اولیه پیام‌ها (بدون polling)
  const messagesQuery = useQuery({
    queryKey: ['messages', conversationId],
    queryFn: () => conversationId ? chatAPI.getMessages(conversationId).then(res => res.data) : [],
    enabled: !!conversationId,
    // ❌ refetchInterval حذف شد - استفاده از WebSocket
  })

  // Set initial messages
  useEffect(() => {
    if (messagesQuery.data) {
      setMessages(messagesQuery.data)
    }
  }, [messagesQuery.data])

  // مدیریت WebSocket
  const handleWebSocketMessage = useCallback((wsMessage: WebSocketMessage) => {
    console.log('📩 Handling WebSocket message:', wsMessage.type)
    
    if (wsMessage.type === 'message') {
      // افزودن پیام جدید به لیست
      setMessages(prev => {
        // جلوگیری از duplicate
        const exists = prev.some(m => m.id === wsMessage.message.id)
        if (exists) return prev
        return [...prev, wsMessage.message]
      })
      
      // Invalidate queries برای sync
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    } else if (wsMessage.type === 'typing') {
      // می‌توانید state typing را به‌روز کنید
      console.log('👤 User typing:', wsMessage.user_id, wsMessage.is_typing)
    } else if (wsMessage.type === 'processing') {
      setIsProcessing(wsMessage.status !== 'completed')
      setProcessingStatus(wsMessage.message || '')
    } else if (wsMessage.type === 'error') {
      console.error('❌ WebSocket error:', wsMessage.message)
      setIsProcessing(false)
    } else if (wsMessage.type === 'connection') {
      console.log('✅ Connected:', wsMessage.message)
    }
  }, [queryClient])

  const { sendMessage: sendWsMessage, isConnected, error: wsError, reconnect } = useWebSocket(
    conversationId,
    getToken(),
    handleWebSocketMessage
  )

  const setTyping = useTypingIndicator(sendWsMessage, isConnected)

  const chat = useCallback((data: ChatRequest) => {
    if (!conversationId || !isConnected) {
      console.warn('⚠️  Cannot send message: not connected')
      return
    }

    // ارسال از طریق WebSocket
    sendWsMessage({
      type: 'chat',
      content: data.message,
      metadata: {
        algorithm: data.algorithm,
        template_id: data.template_id,
        reference_images: data.reference_images
      }
    })
  }, [conversationId, isConnected, sendWsMessage])

  const sendMessageMutation = useMutation({
    mutationFn: ({ conversationId, data }: { conversationId: string; data: any }) =>
      chatAPI.sendMessage(conversationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages', conversationId] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  return {
    conversation: currentConversation || conversationQuery.data,
    messages,
    isLoading: conversationQuery.isLoading || messagesQuery.isLoading,
    error: conversationQuery.error || messagesQuery.error || wsError,
    isConnected,
    isProcessing,
    processingStatus,
    sendMessage: sendMessageMutation.mutate,
    chat,
    setTyping,
    reconnect,
    isSending: sendMessageMutation.isPending,
    refetchMessages: messagesQuery.refetch,
  }
}

export function useMessages(conversationId: string | null) {
  // این hook حالا deprecated است - از useConversation استفاده کنید
  // که شامل WebSocket support می‌باشد
  const messagesQuery = useQuery({
    queryKey: ['messages', conversationId],
    queryFn: () => conversationId ? chatAPI.getMessages(conversationId).then(res => res.data) : [],
    enabled: !!conversationId,
    // ❌ refetchInterval حذف شد
  })

  return {
    messages: messagesQuery.data || [],
    isLoading: messagesQuery.isLoading,
    error: messagesQuery.error,
    refetch: messagesQuery.refetch,
  }
}
