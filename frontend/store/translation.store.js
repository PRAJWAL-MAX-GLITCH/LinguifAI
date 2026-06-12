import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useTranslationStore = create(
  persist(
    (set, get) => ({
      sourceLang: 'auto',
      targetLang: 'en',
      model: 'gpt-4o',
      tone: 'formal',

      setSourceLang: (lang) => set({ sourceLang: lang }),
      
      setTargetLang: (lang) => set({ targetLang: lang }),
      
      setModel: (model) => set({ model }),
      
      setTone: (tone) => set({ tone }),

      swapLanguages: () => {
        const { sourceLang, targetLang } = get();
        if (sourceLang !== 'auto') {
          set({ sourceLang: targetLang, targetLang: sourceLang });
        }
      },
    }),
    {
      name: 'translation-preferences',
    }
  )
);
