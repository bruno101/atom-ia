import { useState, useRef, useCallback } from 'react';

/**
 * Hook personalizado para síntese de voz (Text-to-Speech)
 * Utiliza a Web Speech API para converter texto em áudio
 */
export const useTextToSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const utteranceRef = useRef(null);

  // Função para limpar texto Markdown para leitura
  const cleanTextForSpeech = useCallback((text) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove negrito **texto**
      .replace(/\*(.*?)\*/g, '$1')     // Remove itálico *texto*
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links [texto](url)
      .replace(/#{1,6}\s/g, '')        // Remove headers #
      .replace(/`([^`]+)`/g, '$1')     // Remove código inline `código`
      .replace(/```[\s\S]*?```/g, '')  // Remove blocos de código
      .replace(/\n+/g, '. ')           // Substitui quebras de linha por pausas
      .trim();
  }, []);

  // Inicia a leitura do texto
  const speak = useCallback((text) => {
    if (!('speechSynthesis' in window)) {
      console.warn('Text-to-Speech não suportado neste navegador');
      return;
    }

    // Para qualquer leitura em andamento
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const cleanText = cleanTextForSpeech(text);
    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utteranceRef.current = utterance;

    // Configurações da voz
    utterance.lang = 'pt-BR';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    // Eventos
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    // Inicia a síntese
    window.speechSynthesis.speak(utterance);
  }, [isSpeaking, cleanTextForSpeech]);

  // Para a leitura
  const stop = useCallback(() => {
    if (window.speechSynthesis && isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, [isSpeaking]);

  // Verifica se o navegador suporta Text-to-Speech
  const isSupported = 'speechSynthesis' in window;

  return {
    isSpeaking,
    speak,
    stop,
    isSupported
  };
};