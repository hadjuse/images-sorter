// API configuration - hardcoded for development
export const API_BASE_URL = 'http://127.0.0.1:8000';

// Debug logging
console.log('API Configuration:', {
  hostname: window.location.hostname,
  port: window.location.port,
  API_BASE_URL: API_BASE_URL
});

export const API_ENDPOINTS = {
  PROCESS_IMAGE: `${API_BASE_URL}/process/image`,
  PROCESS_IMAGE_STREAM: `${API_BASE_URL}/process/image/stream`,
  PROCESS_FOLDER: `${API_BASE_URL}/process/folder`,
  HEALTH: `${API_BASE_URL}/health`,
} as const;