import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

/**
 * Fetch all documents for the current user.
 */
export const useDocuments = () => {
  return useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const { data } = await apiClient.get('/documents');
      return data;
    },
  });
};

/**
 * Poll a single document by ID for status updates.
 * Automatically refetches every 3 seconds while status is pending or processing.
 */
export const useDocumentStatus = (docId) => {
  return useQuery({
    queryKey: ['documents', docId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/documents/${docId}`);
      return data;
    },
    enabled: !!docId,
    // Refetch every 3 seconds while not in a terminal state
    refetchInterval: (data) => {
      if (!data) return 3000;
      const terminalStates = ['completed', 'failed'];
      return terminalStates.includes(data.status) ? false : 3000;
    },
  });
};

/**
 * Upload a document for translation.
 */
export const useUploadDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ file, targetLanguage, tone, model, sourceLanguage = 'auto' }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('target_language', targetLanguage);
      formData.append('source_language', sourceLanguage);
      formData.append('tone', tone);
      formData.append('model', model);

      const { data } = await apiClient.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};

/**
 * Delete a document by ID.
 */
export const useDeleteDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (docId) => {
      const { data } = await apiClient.delete(`/documents/${docId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};

/**
 * Download translated document — returns a blob URL trigger.
 */
export const downloadDocument = async (docId, originalFilename) => {
  const response = await apiClient.get(`/documents/${docId}/download`, {
    responseType: 'blob',
  });

  const ext = response.headers['content-disposition']
    ?.match(/filename="(.+)"/)?.[1]
    ?.split('.')
    .pop() || 'txt';

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `translated_${originalFilename}`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};
