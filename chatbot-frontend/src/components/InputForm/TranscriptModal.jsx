import { faCopy, faFilePdf, faPrint, faTimes, faVolumeUp, faStop, faSpinner } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkBreaks from 'remark-breaks';
import styles from "./TranscriptModal.module.css";

const TranscriptModal = ({ isOpen, onClose, transcriptText, isTranscribing }) => {
  const [isReading, setIsReading] = useState(false);
  
  if (!isOpen) return null;

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

  const readTranscript = () => {
    if (isReading) {
      window.speechSynthesis.cancel();
      setIsReading(false);
    } else {
      const utterance = new SpeechSynthesisUtterance(transcriptText);
      utterance.lang = 'pt-BR';
      utterance.onend = () => setIsReading(false);
      window.speechSynthesis.speak(utterance);
      setIsReading(true);
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h3>Transcrição</h3>
          <button onClick={onClose} className={styles.closeModal}>
            <FontAwesomeIcon icon={faTimes} />
          </button>
        </div>
        <div className={styles.modalContent}>
          {isTranscribing ? (
            <div className={styles.progressContainer}>
              <FontAwesomeIcon icon={faSpinner} spin size="3x" />
              <p>Transcrevendo...</p>
            </div>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkBreaks]}>{transcriptText}</ReactMarkdown>
          )}
        </div>
        <div className={styles.modalActions}>
          <button onClick={readTranscript} className={styles.actionButton} disabled={isTranscribing}>
            <FontAwesomeIcon icon={isReading ? faStop : faVolumeUp} /> {isReading ? 'Parar' : 'Ler'}
          </button>
          <button onClick={copyToClipboard} className={styles.actionButton} disabled={isTranscribing}>
            <FontAwesomeIcon icon={faCopy} /> Copiar
          </button>
          <button onClick={exportToPDF} className={styles.actionButton} disabled={isTranscribing}>
            <FontAwesomeIcon icon={faFilePdf} /> Exportar PDF
          </button>
          <button onClick={printTranscript} className={styles.actionButton} disabled={isTranscribing}>
            <FontAwesomeIcon icon={faPrint} /> Imprimir
          </button>
        </div>
      </div>
    </div>
  );
};

export default TranscriptModal;
