import { faBolt, faLightbulb, faSearch, faChevronUp, faMicrophone, faStop, faPaperclip, faPen } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState, useRef, useEffect } from "react";
import { useSpeechRecognition } from "../../hooks/useSpeechRecognition";
import { FileUploadArea } from "../../features/fileUpload";
import { transcribeFile } from "../../features/fileUpload/fileProcessor";
import FileThumbnail from "./FileThumbnail";
import TranscriptModal from "./TranscriptModal";
import styles from "./InputForm.module.css"; 

const InputForm = ({ input, setInput, onSubmit, isLoading, selectedModel = 'flash', onModelChange, setFileMetadata, attachedFile, setAttachedFile }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showTranscriptModal, setShowTranscriptModal] = useState(false);
  const [transcriptText, setTranscriptText] = useState("");
  const [isTranscribing, setIsTranscribing] = useState(false);
  const dropdownRef = useRef(null);
  const { isListening, startListening, stopListening, isSupported } = useSpeechRecognition();

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

  // Abre modal e inicia transcrição
  const handleShowTranscript = async () => {
    setShowTranscriptModal(true);
    setIsTranscribing(true);
    setTranscriptText("");
    
    try {
      const transcription = await transcribeFile(attachedFile);
      setTranscriptText(transcription);
    } catch (error) {
      setTranscriptText(`Erro ao transcrever: ${error.message}`);
    } finally {
      setIsTranscribing(false);
    }
  };

  // Verifica se o arquivo é áudio ou vídeo
  const isAudioOrVideo = () => {
    if (!attachedFile) return false;
    const fileName = attachedFile.name.toLowerCase();
    const fileType = attachedFile.type.toLowerCase();
    const formatosAudio = process.env.REACT_APP_FORMATOS_SUPORTADOS_AUDIO?.split(',') || [];
    const formatosVideo = process.env.REACT_APP_FORMATOS_SUPORTADOS_VIDEO?.split(',') || [];
    
    return fileType.startsWith('audio/') || fileType.startsWith('video/') ||
           formatosAudio.some(ext => fileName.endsWith(ext)) ||
           formatosVideo.some(ext => fileName.endsWith(ext));
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
      {attachedFile && isAudioOrVideo() && (
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
      />
    </div>
  );
};

export default InputForm;
