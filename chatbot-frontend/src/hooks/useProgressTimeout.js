import { useRef, useCallback } from 'react';
import { PROGRESS_CONFIG } from '../config/progressConfig';

export const useProgressTimeout = (isLoading, partialResponse, setCurrentProgressMessage) => {
  const progressTimeoutRef = useRef(null);
  const lastProgressUpdateRef = useRef(null);
  const isLoadingRef = useRef(isLoading);
  const partialResponseRef = useRef(partialResponse);

  // Atualiza refs sempre que os valores mudam
  isLoadingRef.current = isLoading;
  partialResponseRef.current = partialResponse;

  const generateProgressMessage = useCallback(() => {
    const message = PROGRESS_CONFIG.MESSAGES[Math.floor(Math.random() * PROGRESS_CONFIG.MESSAGES.length)];
    console.log('🎲 PROGRESS: Generated message:', message);
    return message;
  }, []);

  const startProgressTimeout = useCallback(() => {
    console.log('⏰ PROGRESS: Starting timeout, isLoading:', isLoadingRef.current, 'partialResponse:', !!partialResponseRef.current, 'timeout:', PROGRESS_CONFIG.TIMEOUT_SECONDS + 's');
    
    if (progressTimeoutRef.current) {
      console.log('🔄 PROGRESS: Clearing existing timeout');
      clearTimeout(progressTimeoutRef.current);
    }
    
    progressTimeoutRef.current = setTimeout(() => {
      console.log('⏰ PROGRESS: Timeout triggered! isLoading:', isLoadingRef.current, 'partialResponse:', !!partialResponseRef.current);
      if (isLoadingRef.current && !partialResponseRef.current) {
        const message = generateProgressMessage();
        console.log('📝 PROGRESS: Setting auto message:', message);
        setCurrentProgressMessage(message);
        lastProgressUpdateRef.current = Date.now();
        startProgressTimeout();
      } else {
        console.log('❌ PROGRESS: Timeout ignored - not loading or has partial response');
      }
    }, PROGRESS_CONFIG.TIMEOUT_SECONDS * 1000);
  }, [setCurrentProgressMessage, generateProgressMessage]);

  const updateProgressMessage = useCallback((message) => {
    console.log('📨 PROGRESS: Updating message:', message, 'isLoading:', isLoadingRef.current, 'partialResponse:', !!partialResponseRef.current);
    setCurrentProgressMessage(message);
    lastProgressUpdateRef.current = Date.now();
    if (isLoadingRef.current && !partialResponseRef.current) {
      console.log('🔄 PROGRESS: Restarting timeout after message update');
      startProgressTimeout();
    }
  }, [setCurrentProgressMessage, startProgressTimeout]);

  const clearProgressTimeout = useCallback(() => {
    console.log('🛑 PROGRESS: Clearing timeout');
    if (progressTimeoutRef.current) {
      clearTimeout(progressTimeoutRef.current);
      progressTimeoutRef.current = null;
    }
  }, []);

  return {
    startProgressTimeout,
    updateProgressMessage,
    clearProgressTimeout
  };
};