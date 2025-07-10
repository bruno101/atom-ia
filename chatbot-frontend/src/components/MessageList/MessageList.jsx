import ChatMessage from "../ChatMessage/ChatMessage";
import LoaderIcon from "../../icons/LoaderIcon";
import ArchiveIcon from "../../icons/ArchiveIcon";
import styles from "./MessageList.module.css";

const MessageList = ({ messages, isLoading, scrollRef }) => (
  <div className={styles.messagesArea} ref={scrollRef}>
    <div className={styles.messagesContainer}>
      {messages.map((m) => (
        <ChatMessage key={m.id} message={m} />
      ))}
      {isLoading && (
        <div className={`${styles.message} ${styles.messageAssistant}`}>
          <div className={`${styles.messageAvatar} ${styles.messageAvatarBot}`}>
            <ArchiveIcon />
          </div>
          <div className={`${styles.messageBubble} ${styles.bubbleAssistant}`}>
            <div className={styles.loadingContent}>
              <LoaderIcon />
              <span>Consultando banco de dados AtoM...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  </div>
);

export default MessageList;
