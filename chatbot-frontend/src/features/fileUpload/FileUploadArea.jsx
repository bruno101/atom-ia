import { useState, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCloudUploadAlt, faFile, faTimes, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { useFileUpload } from './useFileUpload';
import styles from './FileUploadArea.module.css';

console.log('ENV TEXTO:', process.env.REACT_APP_FORMATOS_SUPORTADOS_TEXTO);
console.log('ENV AUDIO:', process.env.REACT_APP_FORMATOS_SUPORTADOS_AUDIO);
console.log('ENV VIDEO:', process.env.REACT_APP_FORMATOS_SUPORTADOS_VIDEO);
console.log('ENV IMAGEM:', process.env.REACT_APP_FORMATOS_SUPORTADOS_IMAGEM);

const acceptedFormats = [
  ...(process.env.REACT_APP_FORMATOS_SUPORTADOS_TEXTO?.split(',') || []),
  ...(process.env.REACT_APP_FORMATOS_SUPORTADOS_AUDIO?.split(',') || []),
  ...(process.env.REACT_APP_FORMATOS_SUPORTADOS_VIDEO?.split(',') || []),
  ...(process.env.REACT_APP_FORMATOS_SUPORTADOS_IMAGEM?.split(',') || [])
].join(', ');

console.log('Accept formats:', acceptedFormats);

/**
 * Componente para upload de arquivos com drag & drop
 */
const FileUploadArea = ({ onFileProcessed, disabled }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const { isProcessing, uploadedFile, handleFileUpload, clearFile } = useFileUpload();

  // Manipula drag over
  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled && !isProcessing) {
      setIsDragOver(true);
    }
  };

  // Manipula drag leave
  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  // Manipula drop de arquivo
  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragOver(false);

    if (disabled || isProcessing) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await processFile(files[0]);
    }
  };

  // Manipula seleção de arquivo
  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      await processFile(files[0]);
    }
  };

  // Processa arquivo
  const processFile = async (file) => {
    try {
      const result = await handleFileUpload(file, (result) => {
        onFileProcessed?.(result, file);
      });
      console.log('Arquivo processado:', result);
    } catch (error) {
      alert(error.message);
      clearFile();
    }
  };

  // Abre seletor de arquivo
  const openFileSelector = () => {
    if (!disabled && !isProcessing) {
      fileInputRef.current?.click();
    }
  };

  // Remove arquivo
  const removeFile = () => {
    clearFile();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className={styles.uploadContainer}>
      {uploadedFile ? (
        // Arquivo carregado
        <div className={styles.filePreview}>
          <FontAwesomeIcon icon={faFile} className={styles.fileIcon} />
          <span className={styles.fileName}>{uploadedFile.name}</span>
          {isProcessing ? (
            <FontAwesomeIcon icon={faSpinner} className={styles.spinner} spin />
          ) : (
            <button
              onClick={removeFile}
              className={styles.removeButton}
              title="Remover arquivo"
            >
              <FontAwesomeIcon icon={faTimes} />
            </button>
          )}
        </div>
      ) : (
        // Área de upload
        <div
          className={`${styles.uploadArea} ${isDragOver ? styles.dragOver : ''} ${disabled ? styles.disabled : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={openFileSelector}
        >
          <FontAwesomeIcon icon={faCloudUploadAlt} className={styles.uploadIcon} />
          <span className={styles.uploadText}>
            Arraste um arquivo ou clique para selecionar
          </span>
          <span className={styles.supportedFormats}>
            vídeo, imagem, áudio, pdf
          </span>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedFormats}
        onChange={handleFileSelect}
        className={styles.hiddenInput}
        disabled={disabled || isProcessing}
      />
    </div>
  );
};

export default FileUploadArea;