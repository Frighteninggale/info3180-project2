import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: `${API_URL}/api`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' }
})

// Auth
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  check: () => api.get('/auth/check'),
  me: () => api.get('/auth/me'),
}

// Profiles
export const profilesAPI = {
  create: (formData) => api.post('/profiles', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getMe: () => api.get('/profiles/me'),
  updateMe: (formData) => api.put('/profiles/me', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getById: (userId) => api.get(`/profiles/${userId}`),
  browse: () => api.get('/profiles/browse'),
  getPictureUrl: (filename) => filename ? `${API_URL}/api/profiles/picture/${filename}` : null,
}

// Matches
export const matchesAPI = {
  action: (targetUserId, action) => api.post('/matches/action', { target_user_id: targetUserId, action }),
  getMutual: () => api.get('/matches/mutual'),
  getCount: () => api.get('/matches/count'),
  getStatus: (targetUserId) => api.get(`/matches/status/${targetUserId}`),
}

// Messages
export const messagesAPI = {
  send: (receiverId, content) => api.post('/messages/send', { receiver_id: receiverId, content }),
  getConversation: (otherUserId) => api.get(`/messages/conversation/${otherUserId}`),
  getConversations: () => api.get('/messages/conversations'),
}

// Search
export const searchAPI = {
  search: (params) => api.get('/search', { params }),
  getInterests: () => api.get('/search/interests'),
}

// Favourites
export const favouritesAPI = {
  getAll: () => api.get('/favourites'),
  add: (profileId) => api.post('/favourites', { profile_id: profileId }),
  remove: (profileId) => api.delete(`/favourites/${profileId}`),
  check: (profileId) => api.get(`/favourites/check/${profileId}`),
}

export default api
