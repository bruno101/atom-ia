import { faCog, faSearch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import styles from "./InputForm.module.css"; 

const InputForm = ({ input, setInput, onSubmit, isLoading }) => (
  <form onSubmit={onSubmit} className={styles.inputForm}>
    <a
      href="http://localhost:63001/index.php/informationobject/browse?query="
      className={`${styles.settingsButton} ${styles.tooltip}`}
    >
      <FontAwesomeIcon icon={faCog} />
      <span className={styles.tooltipText}>Pesquisa normal</span>
    </a>
    <div className={styles.inputContainer}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Digite sua consulta..."
        className={styles.inputField}
        disabled={isLoading}
      />
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

export default InputForm;
