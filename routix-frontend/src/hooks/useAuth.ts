import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/lib/store'
import { authAPI, userAPI } from '@/lib/api'
import { User, AuthTokens } from '@/types'

export function useAuth() {
  const { user, isAuthenticated, login, logout, updateUser } = useAuthStore()
  const queryClient = useQueryClient()

  const loginMutation = useMutation({
    mutationFn: authAPI.login,
    onSuccess: (response) => {
      const data = response.data
      login(data.user, {
        access_token: data.access_token,
        refresh_token: data.refresh_token
      })
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  const registerMutation = useMutation({
    mutationFn: authAPI.register,
    onSuccess: (response) => {
      const data = response.data
      login(data.user, {
        access_token: data.access_token,
        refresh_token: data.refresh_token
      })
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  const logoutMutation = useMutation({
    mutationFn: authAPI.logout,
    onSuccess: () => {
      logout()
      queryClient.clear()
    },
    onError: () => {
      // Even if logout fails on server, clear local state
      logout()
      queryClient.clear()
    },
  })

  const profileQuery = useQuery({
    queryKey: ['user', 'profile'],
    queryFn: () => userAPI.getProfile().then(res => res.data),
    enabled: isAuthenticated,
  })

  const updateProfileMutation = useMutation({
    mutationFn: authAPI.updateProfile,
    onSuccess: (data) => {
      updateUser(data.data)
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  const changePasswordMutation = useMutation({
    mutationFn: authAPI.changePassword,
  })

  return {
    user,
    isAuthenticated,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    updateProfile: updateProfileMutation.mutate,
    changePassword: changePasswordMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    isUpdatingProfile: updateProfileMutation.isPending,
    isChangingPassword: changePasswordMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
    profileData: profileQuery.data,
    isLoadingProfile: profileQuery.isLoading,
  }
}
