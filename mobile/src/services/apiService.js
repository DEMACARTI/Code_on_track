import axios from 'axios';

const API_URL = 'http://localhost:5000/api'; // Update with your server URL

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async getQRCode(qrId) {
    const response = await this.client.get(`/qr/${qrId}`);
    return response.data;
  }

  async scanQRCode(qrId, scanData) {
    const response = await this.client.post(`/qr/${qrId}/scan`, scanData);
    return response.data;
  }

  async recordData(data) {
    const response = await this.client.post('/data/record', data);
    return response.data;
  }

  async getDataRecords(qrId) {
    const response = await this.client.get(`/data/${qrId}`);
    return response.data;
  }
}

export default new ApiService();
