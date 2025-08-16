import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  company_name: string
  role: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
  company_address?: string
  company_phone?: string
  company_website?: string
  company_logo?: string
  default_currency: string
  default_tax_rate: string
  invoice_prefix: string
  next_invoice_number: string
  stripe_enabled: boolean
  paypal_enabled: boolean
}

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const fullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`
  })

  // Actions
  const setUser = (userData: User) => {
    user.value = userData
  }

  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh
    
    // Store tokens in localStorage
    if (process.client) {
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
    }
  }

  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    
    if (process.client) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  const login = async (username: string, password: string) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await $fetch('/api/auth/login', {
        method: 'POST',
        body: { username, password },
        baseURL: useRuntimeConfig().public.apiBaseUrl
      })

      if (response.access_token && response.refresh_token) {
        setTokens(response.access_token, response.refresh_token)
        setUser(response.user)
        return { success: true, user: response.user }
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (err: any) {
      error.value = err.data?.error || err.message || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData: {
    username: string
    email: string
    password: string
    first_name: string
    last_name: string
    company_name?: string
    company_address?: string
    company_phone?: string
    company_website?: string
    default_currency?: string
    default_tax_rate?: string
    invoice_prefix?: string
  }) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await $fetch('/api/auth/register', {
        method: 'POST',
        body: userData,
        baseURL: useRuntimeConfig().public.apiBaseUrl
      })

      if (response.access_token && response.refresh_token) {
        setTokens(response.access_token, response.refresh_token)
        setUser(response.user)
        return { success: true, user: response.user }
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (err: any) {
      error.value = err.data?.error || err.message || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      // Call logout endpoint if needed
      if (accessToken.value) {
        await $fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken.value}`
          },
          baseURL: useRuntimeConfig().public.apiBaseUrl
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear local state
      user.value = null
      clearTokens()
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await $fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refreshToken.value}`
        },
        baseURL: useRuntimeConfig().public.apiBaseUrl
      })

      if (response.access_token) {
        accessToken.value = response.access_token
        if (process.client) {
          localStorage.setItem('access_token', response.access_token)
        }
        return response.access_token
      } else {
        throw new Error('Failed to refresh token')
      }
    } catch (err) {
      // If refresh fails, logout user
      await logout()
      throw err
    }
  }

  const updateProfile = async (profileData: Partial<User>) => {
    if (!accessToken.value) {
      throw new Error('Not authenticated')
    }

    try {
      isLoading.value = true
      error.value = null

      const response = await $fetch('/api/auth/profile', {
        method: 'PUT',
        body: profileData,
        headers: {
          'Authorization': `Bearer ${accessToken.value}`
        },
        baseURL: useRuntimeConfig().public.apiBaseUrl
      })

      if (response.user) {
        setUser(response.user)
        return { success: true, user: response.user }
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (err: any) {
      error.value = err.data?.error || err.message || 'Profile update failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (currentPassword: string, newPassword: string) => {
    if (!accessToken.value) {
      throw new Error('Not authenticated')
    }

    try {
      isLoading.value = true
      error.value = null

      const response = await $fetch('/api/auth/change-password', {
        method: 'POST',
        body: { current_password: currentPassword, new_password: newPassword },
        headers: {
          'Authorization': `Bearer ${accessToken.value}`
        },
        baseURL: useRuntimeConfig().public.apiBaseUrl
      })

      return { success: true, message: response.message }
    } catch (err: any) {
      error.value = err.data?.error || err.message || 'Password change failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const loadStoredTokens = () => {
    if (process.client) {
      const storedAccess = localStorage.getItem('access_token')
      const storedRefresh = localStorage.getItem('refresh_token')
      
      if (storedAccess && storedRefresh) {
        accessToken.value = storedAccess
        refreshToken.value = storedRefresh
        return true
      }
    }
    return false
  }

  const initializeAuth = async () => {
    if (loadStoredTokens()) {
      try {
        // Try to get user profile
        const response = await $fetch('/api/auth/profile', {
          headers: {
            'Authorization': `Bearer ${accessToken.value}`
          },
          baseURL: useRuntimeConfig().public.apiBaseUrl
        })

        if (response.user) {
          setUser(response.user)
          return true
        }
      } catch (err) {
        // If profile fetch fails, clear tokens
        clearTokens()
      }
    }
    return false
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    fullName,
    
    // Actions
    setUser,
    setTokens,
    clearTokens,
    login,
    register,
    logout,
    refreshAccessToken,
    updateProfile,
    changePassword,
    loadStoredTokens,
    initializeAuth
  }
})
