// API Service for Backend Communication

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    return this.request('/health');
  }

  // Get features from backend
  async getFeatures() {
    return this.request('/api/features');
  }

  // Send action to backend
  async sendAction(type, data = null) {
    return this.request('/api/actions', {
      method: 'POST',
      body: JSON.stringify({ type, data }),
    });
  }

  // Track analytics event
  async trackEvent(event, properties = {}) {
    return this.request('/api/analytics', {
      method: 'POST',
      body: JSON.stringify({ event, properties }),
    });
  }

  // Get device info
  async getDeviceInfo() {
    return this.request('/api/device-info');
  }

  // Get app settings
  async getSettings() {
    return this.request('/api/settings');
  }
}

export default new ApiService(); 