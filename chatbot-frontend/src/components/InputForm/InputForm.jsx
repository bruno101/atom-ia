import { faBolt, faLightbulb, faSearch, faChevronUp, faMicrophone, faStop, faPaperclip, faPen, faCopy, faFilePdf, faPrint, faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState, useRef, useEffect } from "react";
import { useSpeechRecognition } from "../../hooks/useSpeechRecognition";
import { FileUploadArea } from "../../features/fileUpload";
import FileThumbnail from "./FileThumbnail";
import styles from "./InputForm.module.css"; 

const InputForm = ({ input, setInput, onSubmit, isLoading, selectedModel = 'flash', onModelChange, setFileMetadata, attachedFile, setAttachedFile }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showTranscriptModal, setShowTranscriptModal] = useState(false);
  const dropdownRef = useRef(null);
  const { isListening, startListening, stopListening, isSupported } = useSpeechRecognition();
  
  const transcriptText = "Quisque augue felis, tincidunt quis diam non, finibus efficitur turpis. Maecenas sed venenatis nisi, et posuere turpis. Quisque non neque odio. Morbi venenatis commodo nunc a cursus. Fusce sem nulla, varius eu ante nec";

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const models = {
    flash: { icon: faBolt, name: 'Rápido', description: 'Mais rápido' },
    thinking: { icon: faLightbulb, name: 'Avançado', description: 'Mais preciso' }
  };

  const handleModelSelect = (model) => {
    onModelChange?.(model);
    setIsDropdownOpen(false);
  };

  // Manipula o clique no botão de voz
  const handleVoiceClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening((transcript) => {
        setInput(transcript);
      });
    }
  };

  // Manipula o resultado do processamento de arquivo
  const handleFileProcessed = (result, file) => {
    setInput(result.query);
    setFileMetadata(result.metadata);
    setAttachedFile(file);
    setShowFileUpload(false);
  };

  // Remove arquivo anexado
  const handleRemoveFile = () => {
    setAttachedFile(null);
    setFileMetadata(null);
    setInput('');
  };

  // Manipula clique no ícone de clipe
  const handleClipClick = () => {
    setShowFileUpload(!showFileUpload);
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

  // Manipula drag over no input para mostrar área de upload
  const handleInputDragOver = (e) => {
    e.preventDefault();
    if (!isLoading) {
      setShowFileUpload(true);
    }
  };

  return (
    <div className={styles.inputContainer}>
      {attachedFile && (
        <FileThumbnail 
          file={attachedFile}
          onRemove={handleRemoveFile}
        />
      )}
      {showFileUpload && (
        <FileUploadArea 
          onFileProcessed={handleFileProcessed}
          disabled={isLoading}
        />
      )}
      <form onSubmit={onSubmit} className={styles.inputForm}>
      <div className={styles.modelSelector} ref={dropdownRef}>
        <button
          type="button"
          className={styles.modelButton}
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        >
          <FontAwesomeIcon icon={models[selectedModel].icon} />
          <FontAwesomeIcon icon={faChevronUp} className={styles.chevron} />
        </button>
        {isDropdownOpen && (
          <div className={styles.dropdown}>
            {Object.entries(models).map(([key, model]) => (
              <button
                key={key}
                type="button"
                className={`${styles.dropdownItem} ${selectedModel === key ? styles.selected : ''}`}
                onClick={() => handleModelSelect(key)}
              >
                <FontAwesomeIcon icon={model.icon} />
                <div className={styles.modelInfo}>
                  <span className={styles.modelName}>{model.name}</span>
                  <span className={styles.modelDescription}>{model.description}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    <div 
      className={styles.inputField}
      onDragOver={handleInputDragOver}
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={isListening ? "Ouvindo..." : "Digite sua consulta..."}
        className={styles.textInput}
        disabled={isLoading}
        aria-label="Digite seu nome completo"
      />
      {attachedFile && (
        <button
          type="button"
          onClick={() => setShowTranscriptModal(true)}
          className={styles.transcribeButton}
          disabled={isLoading}
          title="Transcrever"
        >
          <FontAwesomeIcon icon={faPen} />
        </button>
      )}
      <button
        type="button"
        onClick={handleClipClick}
        className={styles.clipButton}
        disabled={isLoading}
        title="Anexar arquivo"
      >
        <FontAwesomeIcon icon={faPaperclip} />
      </button>
      {isSupported && (
        <button
          type="button"
          onClick={handleVoiceClick}
          className={`${styles.voiceButton} ${isListening ? styles.listening : ''}`}
          disabled={isLoading}
          title={isListening ? "Parar gravação" : "Busca por voz"}
        >
          <FontAwesomeIcon icon={isListening ? faStop : faMicrophone} />
        </button>
      )}
    </div>
    <button
      type="submit"
      disabled={!input.trim() || isLoading}
      className={styles.submitButton}
    >
      <FontAwesomeIcon icon={faSearch} />
    </button>
      </form>
      
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

export default InputForm;
