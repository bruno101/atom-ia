import { useState, useRef, useCallback } from 'react';

/**
 * Hook personalizado para reconhecimento de voz
 * Utiliza a Web Speech API para transcrever áudio em texto
 */
export const useSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef(null);

  // Inicializa o reconhecimento de voz
  const initializeRecognition = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('Reconhecimento de voz não suportado neste navegador');
      return null;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'pt-BR';
    
    return recognition;
  }, []);

  // Inicia a gravação de voz
  const startListening = useCallback((onResult) => {
    if (isListening) return;

    const recognition = initializeRecognition();
    if (!recognition) return;

    recognitionRef.current = recognition;
    setIsListening(true);
    setTranscript('');

    recognition.onresult = (event) => {
      const result = event.results[0][0].transcript;
      setTranscript(result);
      onResult?.(result);
    };

    recognition.onerror = (event) => {
      console.error('Erro no reconhecimento de voz:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  }, [isListening, initializeRecognition]);

  // Para a gravação de voz
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  }, [isListening]);

  // Verifica se o navegador suporta reconhecimento de voz
  const isSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    isSupported
  };
};