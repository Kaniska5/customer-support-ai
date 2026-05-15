import api from '@/api/axios'
import type { AuthResponse, TokenResponse, User } from '@/types'

export const authApi = {
  signup: (data: { email: string; password: string; full_name: string; phone?: string }) =>
    api.post<{ message: string; detail?: string }>('/auth/signup', data),

  verifyOtp: (data: { email: string; otp_code: string; purpose?: string }) =>
    api.post<{ message: string }>('/auth/verify-otp', data),

  login: (data: { email: string; password: string }) =>
    api.post<AuthResponse>('/auth/login', data),

  logout: (refresh_token: string) =>
    api.post<{ message: string }>('/auth/logout', { refresh_token }),

  refresh: (refresh_token: string) =>
    api.post<TokenResponse>('/auth/refresh', { refresh_token }),

  forgotPassword: (email: string) =>
    api.post<{ message: string; detail?: string }>('/auth/forgot-password', { email }),

  resetPassword: (data: { token: string; new_password: string }) =>
    api.post<{ message: string }>('/auth/reset-password', data),

  me: () => api.get<User>('/auth/me'),
}

export const ordersApi = {
  list: (params?: { page?: number; page_size?: number; status?: string }) =>
    api.get('/orders/', { params }),

  getById: (id: string) => api.get(`/orders/${id}`),
}

export const ticketsApi = {
  create: (data: { subject: string; description?: string; priority?: string }) =>
    api.post('/tickets/', data),

  list: (params?: { status?: string }) => api.get('/tickets/', { params }),

  getById: (id: string) => api.get(`/tickets/${id}`),
}

export const chatApi = {
  sendMessage: (data: { session_id: string; ticket_id?: string; message: string }) =>
    api.post('/chat/message', data),
}

export const analyticsApi = {
  summary: () => api.get('/analytics/summary'),
}
