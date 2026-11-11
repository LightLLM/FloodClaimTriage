import { create } from 'zustand'
import { api } from '@/lib/api'
import type { User, LoginRequest } from '@/types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (credentials: LoginRequest) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.login(credentials)
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)

      set({
        user: {
          id: response.user_id,
          email: response.email,
          full_name: response.full_name,
          role: response.role as any,
          is_active: true,
        },
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      })
      throw error
    }
  },

  logout: () => {
    localStorage.clear()
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isAuthenticated: false, user: null })
      return
    }

    try {
      const user = await api.getMe()
      set({ user, isAuthenticated: true })
    } catch {
      localStorage.clear()
      set({ isAuthenticated: false, user: null })
    }
  },
}))
