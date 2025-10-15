import { useState, useCallback } from 'react';
import { processFile } from './fileProcessor';

/**
 * Hook para gerenciar upload e processamento de arquivos
 */
export const useFileUpload = (abortControllerRef) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const acceptedFormats = {
    'application/pdf': ['.pdf'],
    'audio/mpeg': ['.mp3'],
    'audio/mp4': ['.m4a'],
    'audio/wav': ['.wav'],
    'audio/aac': ['.aac'],
    'audio/flac': ['.flac'],
    'audio/ogg': ['.ogg'],
    'video/mp4': ['.mp4'],
    'video/quicktime': ['.mov'],
    'video/mpeg': ['.mpeg', '.mpg'],
    'video/webm': ['.webm'],
    'video/x-msvideo': ['.avi'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/webp': ['.webp'],
    'image/gif': ['.gif'],
    'image/bmp': ['.bmp'],
    'image/heic': ['.heic'],
    'image/heif': ['.heif']
  };

  const isValidFile = useCallback((file) => {
    const fileType = file.type.toLowerCase();
    const fileName = file.name.toLowerCase();
    const allExtensions = ['.pdf', '.mp3', '.mp4', '.m4a', '.wav', '.aac', '.flac', '.ogg', '.mov', '.mpeg', '.mpg', '.webm', '.avi', '.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.heic', '.heif'];
    
    return Object.keys(acceptedFormats).includes(fileType) || allExtensions.some(ext => fileName.endsWith(ext));
  }, []);

  // Processa o arquivo e retorna o texto
  const handleFileUpload = useCallback(async (file, onResult) => {
    console.log('📋 Validando arquivo:', file.name);
    
    if (!isValidFile(file)) {
      console.error('❌ Arquivo inválido:', file.type);
      throw new Error('Formato de arquivo não suportado. Formatos aceitos: PDF, MP3, MP4, M4A, WAV, AAC, FLAC, OGG, MOV, MPEG, WEBM, AVI, JPG, PNG, WEBP, GIF, BMP, HEIC, HEIF.');
    }

    console.log('✅ Arquivo válido, iniciando processamento');
    setIsProcessing(true);
    setUploadedFile(file);

    const controller = new AbortController();
    if (abortControllerRef) {
      abortControllerRef.current = controller;
    }

    try {
      const result = await processFile(file, controller.signal);
      console.log('📦 Resultado recebido do processFile:', result);
      onResult?.(result);
      return result;
    } catch (error) {
      if (error.message === 'Processamento cancelado') {
        console.log('🚫 Processamento cancelado pelo usuário');
        return null;
      }
      console.error('🔴 Erro ao processar arquivo:', error);
      throw error;
    } finally {
      setIsProcessing(false);
      if (abortControllerRef) {
        abortControllerRef.current = null;
      }
    }
  }, [isValidFile, abortControllerRef]);

  // Remove arquivo carregado
  const clearFile = useCallback(() => {
    if (abortControllerRef?.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setUploadedFile(null);
    setIsProcessing(false);
  }, [abortControllerRef]);

  return {
    isProcessing,
    uploadedFile,
    handleFileUpload,
    clearFile,
    isValidFile,
    acceptedFormats: Object.values(acceptedFormats).flat().join(',')
  };
};