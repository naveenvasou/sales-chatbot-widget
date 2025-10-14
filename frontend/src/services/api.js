import axios from 'axios';

const api = axios.create({
  baseURL: '/api', // Uses Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  sendMessage: async (message, sessionId = null) => {
    try {
      const response = await api.post('/chat', {
        message,
        session_id: sessionId,
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  getHistory: async (sessionId) => {
    try {
      const response = await api.get(`/chat/history/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching history:', error);
      throw error;
    }
  },
};

export default api;