import TranslationPanel from '@/components/translation/TranslationPanel';

export default function TranslatePage() {
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-6 flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">AI Translation</h1>
        <p className="text-muted-foreground">
          Translate text across 100+ languages with state-of-the-art AI accuracy and tone detection.
        </p>
      </div>
      
      <TranslationPanel />
    </div>
  );
}
