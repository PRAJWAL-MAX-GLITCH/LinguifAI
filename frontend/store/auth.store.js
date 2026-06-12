import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/lib/axios';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null, // Current User
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setTokens: ({ accessToken, refreshToken }) => {
        set({ accessToken, refreshToken, isAuthenticated: true });
      },

      setUser: (user) => {
        set({ user });
      },

      login: async (email, password) => {
        const { data } = await apiClient.post('/auth/login', { email, password });
        set({
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          isAuthenticated: true,
        });
        await get().fetchUser();
      },

      register: async (userData) => {
        await apiClient.post('/auth/register', userData);
        await get().login(userData.email, userData.password);
      },

      fetchUser: async () => {
        try {
          const { data } = await apiClient.get('/auth/me');
          set({ user: data });
        } catch (error) {
          get().logout();
        }
      },

      logout: async () => {
        try {
          if (get().isAuthenticated) {
             await apiClient.post('/auth/logout');
          }
        } catch (error) {
          // Ignore
        } finally {
          set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        accessToken: state.accessToken, 
        refreshToken: state.refreshToken, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);
