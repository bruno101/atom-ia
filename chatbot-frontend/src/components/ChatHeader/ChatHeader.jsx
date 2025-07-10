import styles from './ChatHeader.module.css';

const ChatHeader = () => (
  
  <div className={styles.chatHeader}>
    <div className={styles.headerContent}>
      <img
        src="/images/sparkle.png"
        alt="Sparkle"
        style={{ width: "2.7em", height: "2.7em", marginRight: "2px" }}
      />
      <div className={styles.headerText}>
        <h1>ModestIA</h1>
        <p>Consulta Arquivística</p>
      </div>
    </div>
  </div>
);

export default ChatHeader;
