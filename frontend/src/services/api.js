/**
 * API service for Leo AI Assistant
 * Handles communication with FastAPI backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making API request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Chat API functions
export const chatAPI = {
  /**
   * Send a message to the assistant
   * @param {string} message - User message
   * @param {string} userId - User ID (optional)
   * @returns {Promise<Object>} Assistant response
   */
  sendMessage: async (message, userId = 'default_user') => {
    const response = await api.post('/chat/send', {
      message,
      user_id: userId,
    });
    return response.data;
  },

  /**
   * Get conversation history
   * @param {number} limit - Maximum number of messages
   * @returns {Promise<Object>} Conversation history
   */
  getHistory: async (limit = 20) => {
    const response = await api.get('/chat/history', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Get memory statistics
   * @returns {Promise<Object>} Memory stats
   */
  getMemoryStats: async () => {
    const response = await api.get('/chat/memory/stats');
    return response.data;
  },

  /**
   * Clear conversation memory
   * @returns {Promise<Object>} Confirmation
   */
  clearMemory: async () => {
    const response = await api.post('/chat/memory/clear');
    return response.data;
  },

  /**
   * Get conversation context
   * @param {string} query - Optional query for context
   * @returns {Promise<Object>} Context data
   */
  getContext: async (query = null) => {
    const response = await api.get('/chat/context', {
      params: query ? { query } : {},
    });
    return response.data;
  },
};

// Agent API functions
export const agentAPI = {
  /**
   * Get agent status
   * @returns {Promise<Object>} Agent status
   */
  getStatus: async () => {
    const response = await api.get('/agent/status');
    return response.data;
  },

  /**
   * Trigger immediate agent update
   * @returns {Promise<Object>} Update confirmation
   */
  triggerUpdate: async () => {
    const response = await api.post('/agent/trigger-update');
    return response.data;
  },

  /**
   * Generate AI insight
   * @returns {Promise<Object>} Generated insight
   */
  generateInsight: async () => {
    const response = await api.post('/agent/generate-insight');
    return response.data;
  },

  /**
   * Get agent metrics
   * @returns {Promise<Object>} Current metrics
   */
  getMetrics: async () => {
    const response = await api.get('/agent/metrics');
    return response.data;
  },
};

// Google Services API functions
export const googleAPI = {
  /**
   * Get Google Calendar events
   * @returns {Promise<Object>} Calendar events
   */
  getCalendar: async () => {
    const response = await api.get('/google/calendar');
    return response.data;
  },

  /**
   * Get Gmail data
   * @returns {Promise<Object>} Gmail data
   */
  getGmail: async () => {
    const response = await api.get('/google/gmail');
    return response.data;
  },

  /**
   * Get Google Tasks
   * @returns {Promise<Object>} Google Tasks
   */
  getTasks: async () => {
    const response = await api.get('/google/tasks');
    return response.data;
  },

  /**
   * Get all Google services data
   * @returns {Promise<Object>} All Google data
   */
  getAll: async () => {
    const response = await api.get('/google/all');
    return response.data;
  },
};

// Health check
export const healthAPI = {
  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

// Export default api instance for custom requests
export default api;