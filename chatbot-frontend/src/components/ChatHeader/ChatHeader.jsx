import styles from './ChatHeader.module.css';

const ChatHeader = () => (
  
  <div className={styles.chatHeader}>
    <div className={styles.headerContent}>
      <img
        src="/images/sparkle-gov.png"
        alt=""
        className={styles.sparkle}
      />
      <div className={styles.headerText}>
        <h1>S<span className={styles.highlight}>IA</span>N</h1>
        <p>Consulta Arquivística com IA</p>
      </div>
    </div>
  </div>
);

export default ChatHeader;
