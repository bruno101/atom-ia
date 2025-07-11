import styles from './ChatHeader.module.css';

const ChatHeader = () => (
  
  <div className={styles.chatHeader}>
    <div className={styles.headerContent}>
      <img
        src="/images/sparkle.png"
        alt=""
        className={styles.sparkle}
      />
      <div className={styles.headerText}>
        <h1>ModestIA</h1>
        <p>Consulta Arquivística</p>
      </div>
    </div>
  </div>
);

export default ChatHeader;
