import { apiService } from './apiService';
import { API_ENDPOINTS } from '../constants';

// Types
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
  };
}

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

// Authentication service
export const authService = {
  // Login user
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiService.post<LoginResponse>(API_ENDPOINTS.auth.login, {
      email,
      password,
    });
    return response;
  },

  // Logout user
  async logout(): Promise<void> {
    try {
      await apiService.post(API_ENDPOINTS.auth.logout);
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      // Always clear local storage
      localStorage.removeItem('auth_token');
    }
  },

  // Validate token
  async validateToken(token: string): Promise<User> {
    const response = await apiService.get<User>(API_ENDPOINTS.auth.validate, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response;
  },

  // Refresh token
  async refreshToken(): Promise<{ token: string }> {
    const response = await apiService.post<{ token: string }>(API_ENDPOINTS.auth.refresh);
    return response;
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = localStorage.getItem('auth_token');
    return !!token;
  },

  // Get current token
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  // Set token
  setToken(token: string): void {
    localStorage.setItem('auth_token', token);
  },

  // Clear token
  clearToken(): void {
    localStorage.removeItem('auth_token');
  },
};