import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://dropout-predictor-2pme.onrender.com/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 45000,
});

const responseCache = new Map();
const pendingRequests = new Map();
export const cachedGet = (url, config = {}, maxAge = 30000) => {
  const params = config.params ? new URLSearchParams(config.params).toString() : '';
  const key = url + '?' + params;
  const cached = responseCache.get(key);
  if (cached && Date.now() - cached.createdAt < maxAge) return Promise.resolve(cached.response);
  if (pendingRequests.has(key)) return pendingRequests.get(key);
  const request = api.get(url, config).then((response) => {
    responseCache.set(key, { response, createdAt: Date.now() });
    return response;
  }).finally(() => pendingRequests.delete(key));
  pendingRequests.set(key, request);
  return request;
};
export const clearApiCache = () => responseCache.clear();

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearApiCache();
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default api;
