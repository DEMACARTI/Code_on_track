import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // QR Code APIs
  async getQRCodes(filters = {}) {
    const response = await this.client.get('/qr', { params: filters })
    return response.data
  }

  async getQRCode(qrId) {
    const response = await this.client.get(`/qr/${qrId}`)
    return response.data
  }

  async generateQRCode(data) {
    const response = await this.client.post('/qr/generate', data)
    return response.data
  }

  async scanQRCode(qrId, scanData) {
    const response = await this.client.post(`/qr/${qrId}/scan`, scanData)
    return response.data
  }

  async updateQRStatus(qrId, status) {
    const response = await this.client.put(`/qr/${qrId}/status`, { status })
    return response.data
  }

  // Data APIs
  async getDataRecords(qrId, params = {}) {
    const response = await this.client.get(`/data/${qrId}`, { params })
    return response.data
  }

  async recordData(data) {
    const response = await this.client.post('/data/record', data)
    return response.data
  }

  async analyzeQRData(qrId) {
    const response = await this.client.post(`/data/${qrId}/analyze`)
    return response.data
  }

  async getAnalytics() {
    const response = await this.client.get('/data/analytics/overview')
    return response.data
  }

  // Notification APIs
  async getNotifications(params = {}) {
    const response = await this.client.get('/notifications', { params })
    return response.data
  }

  async getNotification(id) {
    const response = await this.client.get(`/notifications/${id}`)
    return response.data
  }

  async generateNotifications(qrId) {
    const response = await this.client.post('/notifications/generate', { qrId })
    return response.data
  }

  async updateNotificationStatus(id, status, assignedTo = null) {
    const response = await this.client.put(`/notifications/${id}/status`, {
      status,
      assignedTo,
    })
    return response.data
  }

  async getMaintenanceRecommendations(qrId) {
    const response = await this.client.post('/notifications/maintenance', { qrId })
    return response.data
  }

  // Auth APIs
  async login(credentials) {
    const response = await this.client.post('/auth/login', credentials)
    return response.data
  }

  async register(userData) {
    const response = await this.client.post('/auth/register', userData)
    return response.data
  }
}

export default new ApiService()
