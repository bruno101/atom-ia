import { useState } from "react";
import UserIcon from "../../icons/UserIcon";
import formatTime from "../../utils/formatTime";
import ReactMarkdown from "react-markdown";
import styles from "./ChatMessage.module.css";

const ChatMessage = ({ message }) => {
  const [expandedSections, setExpandedSections] = useState({
    links: false,
    keywords: false,
  });

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Function to extract the slug from URL
  const getSlug = (url) => {
    try {
      const parsed = new URL(url);
      const pathParts = parsed.pathname.split("/").filter((part) => part);
      return pathParts[pathParts.length - 1] || parsed.hostname;
    } catch {
      return (
        url
          .split("/")
          .filter((part) => part)
          .pop() || url
      );
    }
  };

  const isUser = message.role === "user";

  return (
    <div
      className={`${styles.message} ${
        isUser ? styles.messageUser : styles.messageAssistant
      }`}
    >
      {!isUser && (
        <div className={`${styles.messageAvatar} ${styles.messageAvatarBot}`}>
          <img
            src="/images/sparkle-white.png"
            alt=""
            className={styles.sparkleWhite}
          />
        </div>
      )}
      <div
        className={`${styles.messageBubble} ${
          isUser ? styles.bubbleUser : styles.bubbleAssistant
        }`}
      >
        <div className={styles.messageContent}>
          <ReactMarkdown>{message.content}</ReactMarkdown>

          {message.links_analisados && (
            <div className={styles.metadataSection}>
              <button
                className={styles.metadataHeader}
                onClick={() => toggleSection("links")}
              >
                <span>
                  🔗 Links Analisados{" "}
                  <span className={styles.countPill}>69</span>
                </span>
                <span className={styles.chevron}>▶</span>
              </button>
              {expandedSections.links && (
                <div className={styles.metadataContent}>
                  <div className={styles.linkContainer}>
                    {message.links_analisados.map((link) => (
                      <a
                        key={link}
                        href={link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.linkPill}
                      >
                        <span className={styles.linkIcon}>↗</span>
                        {getSlug(link)}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {message.palavras_chave && (
            <div className={styles.metadataSection}>
              <button
                className={styles.metadataHeader}
                onClick={() => toggleSection("keywords")}
                aria-expanded={expandedSections.keywords}
              >
                <span>
                  🏷️ Expressões Pesquisadas{" "}
                  <span className={styles.keywordCountPill}>
                    {message.palavras_chave.length}
                  </span>
                </span>
                <span className={styles.chevron}>▶</span>
              </button>
              {expandedSections.keywords && (
                <div className={styles.metadataContent}>
                  <div className={styles.keywordContainer}>
                    {message.palavras_chave.map((keyword) => (
                      <span key={keyword} className={styles.keywordPill}>
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
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
