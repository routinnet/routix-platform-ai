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
    onSuccess: (data: Conversation[]) => {
      setConversations(data)
    },
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

  const conversationQuery = useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => conversationId ? chatAPI.getConversation(conversationId).then(res => res.data) : null,
    enabled: !!conversationId,
    onSuccess: (data: Conversation) => {
      if (data) {
        setCurrentConversation(data)
      }
    },
  })

  const messagesQuery = useQuery({
    queryKey: ['messages', conversationId],
    queryFn: () => conversationId ? chatAPI.getMessages(conversationId).then(res => res.data) : [],
    enabled: !!conversationId,
  })

  const sendMessageMutation = useMutation({
    mutationFn: ({ conversationId, data }: { conversationId: string; data: any }) =>
      chatAPI.sendMessage(conversationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages', conversationId] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  const chatMutation = useMutation({
    mutationFn: ({ conversationId, data }: { conversationId: string; data: ChatRequest }) =>
      chatAPI.chat(conversationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages', conversationId] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  return {
    conversation: currentConversation || conversationQuery.data,
    messages: messagesQuery.data || [],
    isLoading: conversationQuery.isLoading || messagesQuery.isLoading,
    error: conversationQuery.error || messagesQuery.error,
    sendMessage: sendMessageMutation.mutate,
    chat: chatMutation.mutate,
    isSending: sendMessageMutation.isPending || chatMutation.isPending,
    refetchMessages: messagesQuery.refetch,
  }
}

export function useMessages(conversationId: string | null) {
  const messagesQuery = useQuery({
    queryKey: ['messages', conversationId],
    queryFn: () => conversationId ? chatAPI.getMessages(conversationId).then(res => res.data) : [],
    enabled: !!conversationId,
    refetchInterval: 5000, // Refetch every 5 seconds for real-time updates
  })

  return {
    messages: messagesQuery.data || [],
    isLoading: messagesQuery.isLoading,
    error: messagesQuery.error,
    refetch: messagesQuery.refetch,
  }
}
