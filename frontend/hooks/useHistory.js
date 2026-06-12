import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export const useHistory = (page = 1, limit = 20, filters = {}) => {
  return useQuery({
    queryKey: ['history', page, limit, filters],
    queryFn: async () => {
      const { data } = await apiClient.get('/history', {
        params: { page, limit, ...filters },
      });
      return data;
    },
    keepPreviousData: true,
  });
};

export const useTranslationDetails = (translationId) => {
  return useQuery({
    queryKey: ['history', translationId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/history/${translationId}`);
      return data;
    },
    enabled: !!translationId,
  });
};

export const useToggleStar = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (translationId) => {
      const { data } = await apiClient.patch(`/history/${translationId}/star`);
      return data;
    },
    onSuccess: () => {
      // Refresh the history list to reflect the updated star status
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });
};

export const useDeleteTranslation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (translationId) => {
      const { data } = await apiClient.delete(`/history/${translationId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });
};

export const useClearHistory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.delete('/history');
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });
};
