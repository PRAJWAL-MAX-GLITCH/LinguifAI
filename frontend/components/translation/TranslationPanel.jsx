"use client";

import { useState, useRef } from 'react';
import { ArrowRightLeft, Sparkles, Copy, Check, Info, Mic, Square, Volume2, Loader2 } from 'lucide-react';
import { useTranslate } from '@/hooks/useTranslation';
import { useModels, useLanguages } from '@/hooks/useLanguages';
import { useTranscribe, useSynthesize } from '@/hooks/useSpeech';

export default function TranslationPanel() {
  const [sourceText, setSourceText] = useState("");
  const [sourceLang, setSourceLang] = useState("auto");
  const [targetLang, setTargetLang] = useState("es");
  const [tone, setTone] = useState("formal");
  const [model, setModel] = useState("gpt-4o");
  const [copied, setCopied] = useState(false);
  
  // Audio state
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioPlayerRef = useRef(null);

  const { data: modelsData, isLoading: modelsLoading } = useModels();
  const { data: langsData } = useLanguages();
  
  const translateMutation = useTranslate();
  const transcribeMutation = useTranscribe();
  const synthesizeMutation = useSynthesize();

  const handleTranslate = () => {
    if (!sourceText.trim()) return;
    translateMutation.mutate({
      source_text: sourceText,
      source_language: sourceLang,
      target_language: targetLang,
      tone: tone,
      model: model,
      include_alternatives: true
    });
  };

  const handleSwap = () => {
    if (sourceLang === "auto") return;
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    if (translateMutation.data) {
      setSourceText(translateMutation.data.translated_text);
      translateMutation.reset();
    }
  };

  const handleCopy = () => {
    if (translateMutation.data?.translated_text) {
      navigator.clipboard.writeText(translateMutation.data.translated_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // --- Speech To Text (Microphone) ---
  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        try {
          const transcribedText = await transcribeMutation.mutateAsync(audioBlob);
          setSourceText((prev) => (prev ? prev + " " + transcribedText : transcribedText));
        } catch (error) {
          console.error("Transcription failed", error);
        }
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      alert("Microphone access denied or unavailable.");
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // --- Text To Speech (Audio Player) ---
  const handlePlayAudio = async () => {
    const textToPlay = translateMutation.data?.translated_text;
    if (!textToPlay) return;

    try {
      setIsPlaying(true);
      const audioUrl = await synthesizeMutation.mutateAsync({ text: textToPlay });
      
      if (audioPlayerRef.current) {
        audioPlayerRef.current.src = audioUrl;
        audioPlayerRef.current.play();
        audioPlayerRef.current.onended = () => setIsPlaying(false);
      }
    } catch (error) {
      console.error("Synthesis failed", error);
      setIsPlaying(false);
    }
  };

  const result = translateMutation.data;
  const isTranslating = translateMutation.isPending;

  return (
    <div className="flex flex-col gap-6">
      {/* Top Controls */}
      <div className="flex flex-wrap items-center justify-end gap-4 bg-muted/30 p-3 rounded-lg border">
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Tone</label>
          <select 
            value={tone} 
            onChange={(e) => setTone(e.target.value)}
            className="h-8 rounded-md border border-input bg-background px-2 text-sm focus:ring-1 focus:ring-primary outline-none"
          >
            <option value="formal">Formal</option>
            <option value="casual">Casual</option>
            <option value="technical">Technical</option>
            <option value="literary">Literary</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Model</label>
          <select 
            value={model} 
            onChange={(e) => setModel(e.target.value)}
            disabled={modelsLoading}
            className="h-8 rounded-md border border-input bg-background px-2 text-sm focus:ring-1 focus:ring-primary outline-none max-w-[150px]"
          >
            {modelsData?.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            )) || <option value="gpt-4o">GPT-4o</option>}
          </select>
        </div>
      </div>

      {/* Main Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 min-h-[450px]">
        
        {/* Source Panel */}
        <div className="flex flex-col rounded-xl border bg-card text-card-foreground shadow-sm focus-within:ring-1 focus-within:ring-primary transition-all">
          <div className="flex items-center justify-between border-b px-4 py-3 bg-muted/10">
            <select 
              value={sourceLang} 
              onChange={(e) => setSourceLang(e.target.value)}
              className="bg-transparent font-medium outline-none cursor-pointer max-w-[200px]"
            >
              <option value="auto">Detect Language (Auto)</option>
              {langsData?.map(l => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
            
            <button 
              onClick={handleSwap}
              disabled={sourceLang === "auto"}
              className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition disabled:opacity-50"
              title="Swap Languages"
            >
              <ArrowRightLeft className="w-4 h-4" />
            </button>
          </div>
          
          <textarea 
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            className="flex-1 w-full resize-none p-5 bg-transparent outline-none text-lg leading-relaxed placeholder:text-muted-foreground/60"
            placeholder="Type or paste text here to translate..."
          ></textarea>

          <div className="border-t px-4 py-3 flex justify-between items-center bg-muted/5 gap-2 flex-wrap">
            <div className="flex items-center gap-2">
              <button
                onClick={isRecording ? handleStopRecording : handleStartRecording}
                disabled={transcribeMutation.isPending}
                className={`p-2 rounded-full transition-colors flex items-center justify-center ${
                  isRecording 
                    ? "bg-destructive/20 text-destructive animate-pulse" 
                    : "bg-muted hover:bg-muted-foreground/20 text-muted-foreground"
                }`}
                title={isRecording ? "Stop Dictation" : "Start Dictation"}
              >
                {transcribeMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : isRecording ? (
                  <Square className="w-4 h-4 fill-current" />
                ) : (
                  <Mic className="w-4 h-4" />
                )}
              </button>
              <span className="text-xs text-muted-foreground font-mono">{sourceText.length} / 5000</span>
            </div>
            
            <button 
              onClick={handleTranslate}
              disabled={isTranslating || !sourceText.trim()}
              className="bg-primary text-primary-foreground hover:bg-primary/90 px-5 py-2 rounded-md text-sm font-medium transition flex items-center gap-2 disabled:opacity-50"
            >
              {isTranslating ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Translating...</>
              ) : (
                <><Sparkles className="w-4 h-4" /> Translate</>
              )}
            </button>
          </div>
        </div>

        {/* Target Panel */}
        <div className="flex flex-col rounded-xl border bg-card text-card-foreground shadow-sm relative">
          <div className="flex items-center border-b px-4 py-3 bg-primary/5">
            <select 
              value={targetLang} 
              onChange={(e) => setTargetLang(e.target.value)}
              className="bg-transparent font-medium text-primary outline-none cursor-pointer max-w-[200px]"
            >
              {langsData?.map(l => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>
          
          <div className="flex-1 p-5 text-lg leading-relaxed overflow-y-auto">
            {isTranslating ? (
              <div className="animate-pulse space-y-3 opacity-50">
                <div className="h-4 bg-muted rounded w-3/4"></div>
                <div className="h-4 bg-muted rounded w-full"></div>
                <div className="h-4 bg-muted rounded w-5/6"></div>
              </div>
            ) : result ? (
              <p>{result.translated_text}</p>
            ) : (
              <p className="text-muted-foreground/40 italic">Translation will appear here...</p>
            )}
          </div>

          <div className="border-t px-4 py-3 bg-muted/5 flex flex-wrap gap-y-2 items-center justify-between min-h-[56px]">
            {result ? (
              <>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1.5 text-xs font-medium" title="AI Confidence Score">
                    <div className="flex h-5 items-center justify-center rounded-full bg-green-500/10 px-2 text-green-600 border border-green-500/20">
                      {Math.round(result.confidence_score * 100)}% Accuracy
                    </div>
                  </div>
                  
                  {result.alternative_translations?.length > 0 && (
                     <div className="flex items-center gap-1 text-xs text-muted-foreground group relative cursor-help">
                       <Info className="w-4 h-4" />
                       <span className="hidden sm:inline">Alternatives available</span>
                       <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block w-64 bg-popover text-popover-foreground border rounded-md shadow-lg p-3 z-10 text-sm">
                          <p className="font-semibold mb-1 border-b pb-1">Alternatives:</p>
                          <ul className="list-disc pl-4 space-y-1">
                            {result.alternative_translations.map((alt, i) => (
                              <li key={i}>{alt}</li>
                            ))}
                          </ul>
                       </div>
                     </div>
                  )}
                </div>

                <div className="flex items-center gap-1">
                  {/* Listen Button */}
                  <button 
                    onClick={handlePlayAudio}
                    disabled={synthesizeMutation.isPending || isPlaying}
                    className="p-2 rounded-md hover:bg-primary/10 text-primary transition flex items-center gap-1 disabled:opacity-50"
                    title="Listen to Translation"
                  >
                    {synthesizeMutation.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Volume2 className={`w-4 h-4 ${isPlaying ? "animate-pulse text-green-500" : ""}`} />
                    )}
                  </button>
                  <audio ref={audioPlayerRef} className="hidden" />

                  {/* Copy Button */}
                  <button 
                    onClick={handleCopy}
                    className="p-2 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition"
                    title="Copy Translation"
                  >
                    {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </>
            ) : (
              <span className="text-xs text-muted-foreground opacity-50">Waiting for input...</span>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
