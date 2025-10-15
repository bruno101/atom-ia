import { useState, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCloudUploadAlt, faFile, faTimes, faSpinner, faPen, faCopy, faFilePdf, faPrint } from '@fortawesome/free-solid-svg-icons';
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
const FileUploadArea = ({ onFileProcessed, disabled, abortControllerRef }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [showTranscriptModal, setShowTranscriptModal] = useState(false);
  const fileInputRef = useRef(null);
  const { isProcessing, uploadedFile, handleFileUpload, clearFile } = useFileUpload(abortControllerRef);
  
  const transcriptText = "Quisque augue felis, tincidunt quis diam non, finibus efficitur turpis. Maecenas sed venenatis nisi, et posuere turpis. Quisque non neque odio. Morbi venenatis commodo nunc a cursus. Fusce sem nulla, varius eu ante nec";

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
    console.log('🚀 Iniciando processamento:', file.name);
    try {
      const result = await handleFileUpload(file, (result) => {
        console.log('🎯 Callback onFileProcessed chamado');
        onFileProcessed?.(result, file);
      });
      console.log('✅ Arquivo processado com sucesso:', result);
    } catch (error) {
      console.error('🚫 Erro capturado:', error);
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

  // Funções do modal de transcrição
  const copyToClipboard = () => {
    navigator.clipboard.writeText(transcriptText);
    alert('Texto copiado para a área de transferência!');
  };

  const exportToPDF = () => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head><title>Transcrição</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
          <h2>Transcrição</h2>
          <p>${transcriptText}</p>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const printTranscript = () => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head><title>Transcrição</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
          <h2>Transcrição</h2>
          <p>${transcriptText}</p>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
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
            <div className={styles.buttonGroup}>
              <button
                onClick={() => setShowTranscriptModal(true)}
                className={styles.transcribeButton}
                title="Transcrever"
              >
                <FontAwesomeIcon icon={faPen} />
              </button>
              <button
                onClick={removeFile}
                className={styles.removeButton}
                title="Remover arquivo"
              >
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
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
      
      {/* Modal de Transcrição */}
      {showTranscriptModal && (
        <div className={styles.modalOverlay} onClick={() => setShowTranscriptModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3>Transcrição</h3>
              <button 
                onClick={() => setShowTranscriptModal(false)}
                className={styles.closeModal}
              >
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
            <div className={styles.modalContent}>
              <p>{transcriptText}</p>
            </div>
            <div className={styles.modalActions}>
              <button onClick={copyToClipboard} className={styles.actionButton}>
                <FontAwesomeIcon icon={faCopy} /> Copiar
              </button>
              <button onClick={exportToPDF} className={styles.actionButton}>
                <FontAwesomeIcon icon={faFilePdf} /> Exportar PDF
              </button>
              <button onClick={printTranscript} className={styles.actionButton}>
                <FontAwesomeIcon icon={faPrint} /> Imprimir
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploadArea;