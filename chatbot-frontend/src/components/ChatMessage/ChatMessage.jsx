import ArchiveIcon from "../../icons/ArchiveIcon";
import UserIcon from "../../icons/UserIcon";
import formatTime from "../../utils/formatTime";
import ReactMarkdown from "react-markdown";
import styles from './ChatMessage.module.css';

const ChatMessage = ({ message }) => {
  const isUser = message.role === "user";
  return (
    <div className={`${styles.message} ${isUser ? styles.messageUser : styles.messageAssistant}`}>
      {!isUser && (
        <div className={`${styles.messageAvatar} ${styles.messageAvatarBot}`}>
          <ArchiveIcon />
        </div>
      )}
      <div
        className={`${styles.messageBubble} ${
          isUser ? styles.bubbleUser : styles.bubbleAssistant
        }`}
      >
        <div className={styles.messageContent}>
          <ReactMarkdown
          >
            {message.content}
          </ReactMarkdown>
        </div>
        <div className={styles.messageTime}>
          <div className={styles.messageDot}></div>
          {formatTime(message.timestamp)}
        </div>
      </div>
      {isUser && (
        <div className={`${styles.messageAvatar} ${styles.messageAvatarUser}`}>
          <UserIcon />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
