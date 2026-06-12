import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export const useLanguages = () => {
  return useQuery({
    queryKey: ['languages'],
    queryFn: async () => {
      const { data } = await apiClient.get('/languages');
      return data;
    },
    staleTime: 1000 * 60 * 60 * 24, // Cache static language data for 24 hours
  });
};

export const useModels = () => {
  return useQuery({
    queryKey: ['models'],
    queryFn: async () => {
      const { data } = await apiClient.get('/translate/models');
      return data.models;
    },
    staleTime: 1000 * 60 * 60, // Cache models for 1 hour
  });
};
