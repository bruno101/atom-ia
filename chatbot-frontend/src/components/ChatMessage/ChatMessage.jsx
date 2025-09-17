import { useState } from "react";
import UserIcon from "../../icons/UserIcon";
import formatTime from "../../utils/formatTime";
import ReactMarkdown from "react-markdown";
import styles from "./ChatMessage.module.css";

/**
 * Componente para exibir uma mensagem individual no chat
 * Suporta mensagens do usuário e do assistente com metadados expansíveis
 */
const ChatMessage = ({ message }) => {
  // Estado para controlar quais seções de metadados estão expandidas
  const [expandedSections, setExpandedSections] = useState({
    links: false,
    keywords: false,
  });

  // Alterna a visibilidade de uma seção de metadados
  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Extrai o slug/identificador de uma URL para exibição mais limpa
  const getSlug = (url) => {
    try {
      const parsed = new URL(url);
      const pathParts = parsed.pathname.split("/").filter((part) => part);
      const slug = pathParts[pathParts.length - 1] || parsed.hostname;
      return slug + parsed.search;
    } catch {
      // Fallback para URLs malformadas
      return (
        url
          .split("/")
          .filter((part) => part)
          .pop() || url
      );
    }
  };

  // Determina se a mensagem é do usuário ou do assistente
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
          {/* Renderiza o conteúdo da mensagem com suporte a Markdown */}
          <ReactMarkdown
            components={{
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noopener noreferrer">
                  {children}
                </a>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>

          {/* Seção de links analisados (expansível) */}
          {message.links_analisados && (
            <div className={styles.metadataSection}>
              <button
                className={styles.metadataHeader}
                onClick={() => toggleSection("links")}
              >
                <span>
                  🔗 Links Analisados{" "}
                  <span className={styles.countPill}>{message.links_analisados.length}</span>
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

          {/* Seção de palavras-chave/expressões pesquisadas (expansível) */}
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
        {/* Timestamp da mensagem */}
        <div className={styles.messageTime}>
          <div className={styles.messageDot}></div>
          {formatTime(message.timestamp)}
        </div>
      </div>
      {/* Avatar do usuário (apenas para mensagens do usuário) */}
      {isUser && (
        <div className={`${styles.messageAvatar} ${styles.messageAvatarUser}`}>
          <UserIcon />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
