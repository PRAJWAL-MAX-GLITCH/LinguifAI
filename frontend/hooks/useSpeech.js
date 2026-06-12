import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export const useTranscribe = () => {
  return useMutation({
    mutationFn: async (audioBlob) => {
      const formData = new FormData();
      // Need a filename for the backend to process the extension
      formData.append('file', audioBlob, 'recording.webm');

      const { data } = await apiClient.post('/speech/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data.text;
    },
  });
};

export const useSynthesize = () => {
  return useMutation({
    mutationFn: async ({ text, voice = 'alloy' }) => {
      const response = await apiClient.post('/speech/synthesize', { text, voice }, {
        responseType: 'blob', // Important for handling audio file response
      });
      // Create an object URL from the blob
      return URL.createObjectURL(new Blob([response.data], { type: 'audio/mpeg' }));
    },
  });
};
