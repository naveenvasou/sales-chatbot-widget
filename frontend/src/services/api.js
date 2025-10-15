import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v2',
  headers: { 'Content-Type': 'application/json' },
});

export const chatAPI = {
  // Initialize chat
  init: async () => {
    const { data } = await api.post('/chat/init', {});
    return data;
  },

  // Select category
  selectCategory: async (sessionId, category) => {
    const { data } = await api.post('/chat/select-category', {
      session_id: sessionId,
      category,
    });
    return data;
  },

  // Submit lead
  submitLead: async (sessionId, category, name, email, phone) => {
    const { data } = await api.post('/chat/submit-lead', {
      session_id: sessionId,
      category,
      name,
      email,
      phone,
    });
    return data;
  },

  // Send user input (button/form/text)
  sendInput: async (sessionId, currentState, inputType, inputData) => {
    const { data } = await api.post('/chat/input', {
      session_id: sessionId,
      current_state: currentState,
      input_type: inputType,
      input_data: inputData,
    });
    return data;
  },

  // Back to menu
  backToMenu: async (sessionId) => {
    const { data } = await api.post('/chat/menu', {
      session_id: sessionId,
    });
    return data;
  },

  // End chat
  endChat: async (sessionId) => {
    const { data } = await api.post('/chat/end', { session_id: sessionId });
    return data;
  },
};

export default api;