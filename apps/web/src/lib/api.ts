import axios, { AxiosInstance } from 'axios'
import type {
  LoginRequest,
  LoginResponse,
  Event,
  Property,
  TriageItem,
  PropertyEvidence,
  User,
  ScoreEventResult,
  ReviewScoreResult,
  HealthStatus,
} from '@/types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            try {
              const response = await this.refreshToken(refreshToken)
              localStorage.setItem('access_token', response.access_token)
              localStorage.setItem('refresh_token', response.refresh_token)
              error.config.headers.Authorization = `Bearer ${response.access_token}`
              return this.client.request(error.config)
            } catch {
              localStorage.clear()
              window.location.href = '/login'
            }
          } else {
            localStorage.clear()
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const { data } = await this.client.post<LoginResponse>('/auth/login', credentials)
    return data
  }

  async refreshToken(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    const { data } = await this.client.post('/auth/refresh', { refresh_token: refreshToken })
    return data
  }

  async getMe(): Promise<User> {
    const { data } = await this.client.get<User>('/auth/me')
    return data
  }

  async getEvents(): Promise<Event[]> {
    const { data } = await this.client.get<Event[]>('/events')
    return data
  }

  async getEvent(id: string): Promise<Event> {
    const { data } = await this.client.get<Event>(`/events/${id}`)
    return data
  }

  async createEvent(event: Partial<Event>): Promise<Event> {
    const { data } = await this.client.post<Event>('/events', event)
    return data
  }

  async scoreEvent(eventId: string, forceRescore: boolean = false): Promise<ScoreEventResult> {
    const { data } = await this.client.post<ScoreEventResult>(`/events/${eventId}/score`, null, {
      params: { force_rescore: forceRescore },
    })
    return data
  }

  async getProperties(skip: number = 0, limit: number = 100): Promise<Property[]> {
    const { data } = await this.client.get<Property[]>('/properties', {
      params: { skip, limit },
    })
    return data
  }

  async getProperty(id: string): Promise<Property> {
    const { data } = await this.client.get<Property>(`/properties/${id}`)
    return data
  }

  async getTriageQueue(
    eventId: string,
    options?: {
      priority?: string
      min_probability?: number
      skip?: number
      limit?: number
    }
  ): Promise<TriageItem[]> {
    const { data } = await this.client.get<TriageItem[]>(`/events/${eventId}/triage`, {
      params: options,
    })
    return data
  }

  async getPropertyEvidence(eventId: string, propertyId: string): Promise<PropertyEvidence> {
    const { data } = await this.client.get<PropertyEvidence>(
      `/events/${eventId}/properties/${propertyId}/evidence`
    )
    return data
  }

  async reviewScore(
    scoreId: string,
    action: 'accept' | 'override',
    reason?: string,
    newPriority?: string
  ): Promise<ReviewScoreResult> {
    const { data } = await this.client.post<ReviewScoreResult>(`/scores/${scoreId}/review`, null, {
      params: { action, reason, new_priority: newPriority },
    })
    return data
  }

  async exportTriage(eventId: string): Promise<Blob> {
    const { data } = await this.client.get(`/events/${eventId}/export.csv`, {
      responseType: 'blob',
    })
    return data
  }

  async healthCheck(): Promise<HealthStatus> {
    const { data } = await axios.get<HealthStatus>(`${API_URL}/health`)
    return data
  }
}

export const api = new ApiClient()
