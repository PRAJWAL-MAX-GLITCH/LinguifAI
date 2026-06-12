import axios from 'axios';
import { getSession, signOut } from 'next-auth/react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Access Token
apiClient.interceptors.request.use(
  async (config) => {
    // NextAuth getSession works on the client-side
    const session = await getSession();
    const token = session?.accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle Automatic Refresh Token Logic
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 Unauthorized and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const session = await getSession();
      const refreshToken = session?.refreshToken;

      if (refreshToken) {
        try {
          // Attempt to refresh the token directly via axios to avoid interceptor loop
          const { data } = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          // In NextAuth v4, you can't easily mutate the session tokens from client side directly
          // without triggering a session update event. 
          // However, we can patch the Authorization header for this immediate retry.
          // Note: In production, you'd trigger NextAuth session update here:
          // await updateSession({...}) but for now we'll just log out if it fails completely.
          
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // If refresh fails, log the user out via NextAuth
          await signOut({ callbackUrl: '/login' });
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available, force logout
        await signOut({ callbackUrl: '/login' });
      }
    }

    return Promise.reject(error);
  }
);
