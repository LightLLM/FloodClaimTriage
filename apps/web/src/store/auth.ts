import { create } from 'zustand'
import { api } from '@/lib/api'
import { DEMO_USERS } from '@/lib/demoData'
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
      localStorage.removeItem('demo_mode')

      set({
        user: {
          id: response.user_id,
          email: response.email,
          full_name: response.full_name,
          role: response.role as User['role'],
          is_active: true,
        },
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: unknown) {
      // Fall back to local demo mode when API is unavailable
      const demo = DEMO_USERS[credentials.email]
      if (demo && demo.password === credentials.password) {
        localStorage.setItem('access_token', 'demo-token')
        localStorage.setItem('refresh_token', 'demo-refresh')
        localStorage.setItem('demo_mode', 'true')
        localStorage.setItem('demo_user', JSON.stringify(demo.user))

        set({
          user: {
            id: demo.user.id,
            email: demo.user.email,
            full_name: demo.user.full_name,
            role: demo.user.role as User['role'],
            is_active: true,
          },
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
        return
      }

      const message =
        error && typeof error === 'object' && 'response' in error
          ? String((error as { response?: { data?: { detail?: string } } }).response?.data?.detail)
          : 'Login failed'

      set({
        error: message || 'Login failed',
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

    if (localStorage.getItem('demo_mode') === 'true') {
      const raw = localStorage.getItem('demo_user')
      if (raw) {
        const demoUser = JSON.parse(raw)
        set({
          user: {
            id: demoUser.id,
            email: demoUser.email,
            full_name: demoUser.full_name,
            role: demoUser.role,
            is_active: true,
          },
          isAuthenticated: true,
        })
        return
      }
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
