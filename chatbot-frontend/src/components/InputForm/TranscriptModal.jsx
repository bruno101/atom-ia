import { faCopy, faFilePdf, faPrint, faTimes, faVolumeUp, faStop, faSpinner, faShare } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkBreaks from 'remark-breaks';
import styles from "./TranscriptModal.module.css";

const TranscriptModal = ({ isOpen, onClose, transcriptText, isTranscribing, progressMessage }) => {
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

  const shareTranscript = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Transcrição',
          text: transcriptText
        });
      } catch (error) {
        console.log('Compartilhamento cancelado');
      }
    } else {
      copyToClipboard();
      alert('Texto copiado! Cole onde desejar compartilhar.');
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
          {isTranscribing && !transcriptText ? (
            <div className={styles.progressContainer}>
              <FontAwesomeIcon icon={faSpinner} spin size="3x" />
              <p>{progressMessage || 'Preparando transcrição...'}</p>
            </div>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkBreaks]}>{transcriptText || 'Aguardando transcrição...'}</ReactMarkdown>
          )}
        </div>
        <div className={styles.modalActions}>
          <button onClick={readTranscript} className={styles.actionButton} disabled={isTranscribing} title={isReading ? 'Parar' : 'Ler'}>
            <FontAwesomeIcon icon={isReading ? faStop : faVolumeUp} />
          </button>
          <button onClick={copyToClipboard} className={styles.actionButton} disabled={isTranscribing} title="Copiar">
            <FontAwesomeIcon icon={faCopy} />
          </button>
          <button onClick={shareTranscript} className={styles.actionButton} disabled={isTranscribing} title="Compartilhar">
            <FontAwesomeIcon icon={faShare} />
          </button>
          <button onClick={exportToPDF} className={styles.actionButton} disabled={isTranscribing} title="Exportar PDF">
            <FontAwesomeIcon icon={faFilePdf} />
          </button>
          <button onClick={printTranscript} className={styles.actionButton} disabled={isTranscribing} title="Imprimir">
            <FontAwesomeIcon icon={faPrint} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default TranscriptModal;
