import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_BASE_URL, HTTP_STATUS, ERROR_MESSAGES } from '../constants';

// API response types
interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// Create axios instance
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      return response;
    },
    (error: AxiosError) => {
      const apiError: ApiError = {
        message: ERROR_MESSAGES.GENERIC_ERROR,
        status: error.response?.status || 500,
        details: error.response?.data,
      };

      // Handle specific error cases
      switch (error.response?.status) {
        case HTTP_STATUS.UNAUTHORIZED:
          apiError.message = ERROR_MESSAGES.AUTH_FAILED;
          // Clear auth token on 401
          localStorage.removeItem('auth_token');
          break;
        case HTTP_STATUS.NOT_FOUND:
          apiError.message = 'Resource not found';
          break;
        case HTTP_STATUS.BAD_REQUEST:
          apiError.message = error.response?.data?.message || 'Invalid request';
          break;
        case HTTP_STATUS.INTERNAL_SERVER_ERROR:
          apiError.message = 'Server error. Please try again later.';
          break;
        default:
          if (!navigator.onLine) {
            apiError.message = ERROR_MESSAGES.NETWORK_ERROR;
          }
      }

      return Promise.reject(apiError);
    }
  );

  return client;
};

// Create the API client instance
export const apiClient = createApiClient();

// Generic API methods
export const apiService = {
  // GET request
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await apiClient.get<ApiResponse<T>>(url, { params });
    return response.data.data;
  },

  // POST request
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await apiClient.post<ApiResponse<T>>(url, data);
    return response.data.data;
  },

  // PUT request
  async put<T>(url: string, data?: any): Promise<T> {
    const response = await apiClient.put<ApiResponse<T>>(url, data);
    return response.data.data;
  },

  // DELETE request
  async delete<T>(url: string): Promise<T> {
    const response = await apiClient.delete<ApiResponse<T>>(url);
    return response.data.data;
  },

  // PATCH request
  async patch<T>(url: string, data?: any): Promise<T> {
    const response = await apiClient.patch<ApiResponse<T>>(url, data);
    return response.data.data;
  },

  // File upload
  async upload<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data.data;
  },

  // Download file
  async download(url: string, filename?: string): Promise<void> {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    });

    // Create download link
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  },
};

// Health check
export const healthCheck = async (): Promise<{ status: string; timestamp: string }> => {
  return apiService.get('/api/v1/health');
};

export default apiService;