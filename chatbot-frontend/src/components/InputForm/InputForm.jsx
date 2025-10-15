// Componente de formulário de entrada do chat
// Gerencia input de texto, voz, upload de arquivos e transcrição
import { faBolt, faLightbulb, faSearch, faChevronUp, faMicrophone, faStop, faPaperclip, faPen } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState, useRef, useEffect } from "react";
import { useSpeechRecognition } from "../../hooks/useSpeechRecognition";
import { FileUploadArea } from "../../features/fileUpload";
import { handleTranscribeSSE } from "../../logic/handleTranscribeSSE";
import { getTranscribeEndpoint, isAudioOrVideoFile } from "../../features/fileUpload/fileProcessor";
import FileThumbnail from "./FileThumbnail";
import TranscriptModal from "./TranscriptModal";
import styles from "./InputForm.module.css"; 

const InputForm = ({ input, setInput, onSubmit, isLoading, selectedModel = 'flash', onModelChange, setFileMetadata, attachedFile, setAttachedFile }) => {
  // Estados para controle de UI
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showTranscriptModal, setShowTranscriptModal] = useState(false);
  
  // Estados para transcrição
  const [transcriptText, setTranscriptText] = useState("");
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [progressMessage, setProgressMessage] = useState("");
  
  const dropdownRef = useRef(null);
  const { isListening, startListening, stopListening, isSupported } = useSpeechRecognition();

  // Fecha dropdown ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Configuração dos modelos disponíveis
  const models = {
    flash: { icon: faBolt, name: 'Rápido', description: 'Mais rápido' },
    thinking: { icon: faLightbulb, name: 'Avançado', description: 'Mais preciso' }
  };

  // Seleciona modelo e fecha dropdown
  const handleModelSelect = (model) => {
    onModelChange?.(model);
    setIsDropdownOpen(false);
  };

  // Inicia/para reconhecimento de voz
  const handleVoiceClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening((transcript) => {
        setInput(transcript);
      });
    }
  };

  // Processa arquivo e atualiza estado
  const handleFileProcessed = (result, file) => {
    setInput(result.query);
    setFileMetadata(result.metadata);
    setAttachedFile(file);
    setShowFileUpload(false);
  };

  // Remove arquivo anexado e limpa estado
  const handleRemoveFile = () => {
    setAttachedFile(null);
    setFileMetadata(null);
    setInput('');
  };

  // Alterna visibilidade da área de upload
  const handleClipClick = () => {
    setShowFileUpload(!showFileUpload);
  };

  // Abre modal e inicia transcrição de áudio/vídeo
  const handleShowTranscript = () => {
    setShowTranscriptModal(true);
    setIsTranscribing(true);
    setTranscriptText("");
    setProgressMessage("");
    
    const endpoint = getTranscribeEndpoint(attachedFile);
    
    // Inicia transcrição com streaming SSE
    handleTranscribeSSE(
      attachedFile,
      endpoint,
      (progress) => {
        setProgressMessage(progress);
      },
      (chunk, isFinal) => {
        if (isFinal) {
          console.log('[InputForm] Received FINAL chunk, length:', chunk.length);
          console.log('[InputForm] FINAL chunk preview:', chunk.substring(0, 200));
          // Substitui com transcrição final corrigida
          setTranscriptText(chunk);
          setIsTranscribing(false);
          setProgressMessage("");
        } else {
          // Adiciona chunk parcial
          setTranscriptText(prev => prev + chunk);
        }
      },
      () => {
        console.log('[InputForm] Transcription completed');
        setIsTranscribing(false);
        setProgressMessage("");
      },
      (error) => {
        setTranscriptText(`Erro ao transcrever: ${error.message}`);
        setIsTranscribing(false);
        setProgressMessage("");
      }
    );
  };


  // Mostra área de upload ao arrastar arquivo sobre input
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
      {attachedFile && isAudioOrVideoFile(attachedFile) && (
        <button
          type="button"
          onClick={handleShowTranscript}
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
      
      <TranscriptModal
        isOpen={showTranscriptModal}
        onClose={() => setShowTranscriptModal(false)}
        transcriptText={transcriptText}
        isTranscribing={isTranscribing}
        progressMessage={progressMessage}
      />
    </div>
  );
};

export default InputForm;
