import { useState, useCallback } from 'react';
import { processFile } from './fileProcessor';

/**
 * Hook para gerenciar upload e processamento de arquivos
 */
export const useFileUpload = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  // Formatos aceitos
  const acceptedFormats = {
    'application/pdf': '.pdf',
    'audio/mp3': '.mp3',
    'audio/mpeg': '.mp3',
    'video/mp4': '.mp4',
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp'
  };

  // Verifica se o arquivo é válido
  const isValidFile = useCallback((file) => {
    const fileType = file.type.toLowerCase();
    const fileName = file.name.toLowerCase();
    
    return (
      Object.keys(acceptedFormats).includes(fileType) ||
      fileName.endsWith('.pdf') ||
      fileName.endsWith('.mp3') ||
      fileName.endsWith('.mp4') ||
      fileName.endsWith('.m4a') ||
      fileName.endsWith('.jpg') ||
      fileName.endsWith('.jpeg') ||
      fileName.endsWith('.png') ||
      fileName.endsWith('.webp')
    );
  }, []);

  // Processa o arquivo e retorna o texto
  const handleFileUpload = useCallback(async (file, onResult) => {
    if (!isValidFile(file)) {
      throw new Error('Formato de arquivo não suportado. Use PDF, MP3, MP4, M4A, JPG, PNG ou WEBP.');
    }

    setIsProcessing(true);
    setUploadedFile(file);

    try {
      const result = await processFile(file);
      onResult?.(result);
      return result;
    } catch (error) {
      console.error('Erro ao processar arquivo:', error);
      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [isValidFile]);

  // Remove arquivo carregado
  const clearFile = useCallback(() => {
    setUploadedFile(null);
  }, []);

  return {
    isProcessing,
    uploadedFile,
    handleFileUpload,
    clearFile,
    isValidFile,
    acceptedFormats: Object.values(acceptedFormats).join(',')
  };
};