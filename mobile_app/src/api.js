import axios from 'axios';

// When running on local Android Emulator, Use 10.0.2.2 instead of localhost
// To switch to production, change this to your Render URL: 'https://ai-score-owz2.onrender.com/api'
export const BASE_URL = 'http://10.0.2.2:8000/api'; 

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
