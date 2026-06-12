import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export const useTranslate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (translationData) => {
      const { data } = await apiClient.post('/translate', translationData);
      return data;
    },
    onSuccess: () => {
      // Invalidate history to automatically fetch the newly saved translation
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });
};

export const useBatchTranslate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (batchData) => {
      const { data } = await apiClient.post('/translate/batch', { items: batchData });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });
};

export const useDetectLanguage = () => {
  return useMutation({
    mutationFn: async (text) => {
      const { data } = await apiClient.post('/translate/detect', { text });
      return data;
    },
  });
};
