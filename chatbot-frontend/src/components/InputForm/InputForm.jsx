import { faBolt, faLightbulb, faSearch, faChevronUp, faMicrophone, faStop } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState, useRef, useEffect } from "react";
import { useSpeechRecognition } from "../../hooks/useSpeechRecognition";
import styles from "./InputForm.module.css"; 

const InputForm = ({ input, setInput, onSubmit, isLoading, selectedModel = 'flash', onModelChange }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
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

  return (
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
    <div className={styles.inputContainer}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={isListening ? "Ouvindo..." : "Digite sua consulta..."}
        className={styles.inputField}
        disabled={isLoading}
      />
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
  );
};

export default InputForm;
