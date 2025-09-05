// components/MessageList/MessageList.jsx
import ChatMessage from "../ChatMessage/ChatMessage";
import LoaderIcon from "../../icons/LoaderIcon";
import styles from "./MessageList.module.css";

const MessageList = ({ messages, isLoading, streamedMessage }) => {
  return (
    <div className={styles.messagesArea}>
      <div className={styles.messagesContainer}>
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}

        {(isLoading || streamedMessage) && (
          <div className={`${styles.message} ${styles.messageAssistant}`}>
            <div
              className={`${styles.messageAvatar} ${styles.messageAvatarBot}`}
            >
              <img
                src="/images/sparkle-white.png"
                alt=""
                className={styles.sparkleWhite}
              />
            </div>
            <div
              className={`${styles.messageBubble} ${styles.bubbleAssistant}`}
            >
              <div className={styles.loadingContent}>
                <LoaderIcon className={styles.spinner} />
                <span>
                  {streamedMessage || "Aguardando resposta..."}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageList;
