import { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronDown, faChevronRight } from '@fortawesome/free-solid-svg-icons';
import ExternalLinkIcon from "../../icons/ExternalLinkIcon";
import { getAllConversations, deleteConversation } from "../../utils/conversationStorage";
import styles from './Sidebar.module.css';

const Sidebar = ({ suggestedLinks, onNewConversation, onLoadConversation, currentConversationId }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [conversationsExpanded, setConversationsExpanded] = useState(true);
  const [linksExpanded, setLinksExpanded] = useState(true);

  const isExpanded = isHovered || isPinned;

  useEffect(() => {
    const loadConversations = () => {
      const allConvs = getAllConversations();
      const convArray = Object.values(allConvs).sort((a, b) => 
        new Date(b.updatedAt) - new Date(a.updatedAt)
      );
      setConversations(convArray);
    };
    loadConversations();
    const interval = setInterval(loadConversations, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleTogglePin = () => {
    setIsPinned(!isPinned);
  };

  const handleDeleteConversation = (e, convId) => {
    e.stopPropagation();
    deleteConversation(convId);
    setConversations(prev => prev.filter(c => c.id !== convId));
    if (convId === currentConversationId) {
      onNewConversation();
    }
  };

  return (
    <div 
      className={`${styles.sidebar} ${!isExpanded ? styles.collapsed : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className={styles.sidebarHeader}>
        <button 
          className={styles.toggleButton}
          onClick={handleTogglePin}
          title={isPinned ? "Destravar sidebar" : "Travar sidebar expandida"}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path 
              d={isPinned ? "M16 4v12l-4-2-4 2V4M6 2h12a2 2 0 0 1 2 2v16l-8-4-8 4V4a2 2 0 0 1 2-2z" : "M3 12h18m-9-9l9 9-9 9"}
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </svg>
        </button>
        {isExpanded && (
          <img
            src="/images/an-logo.webp"
            alt="Logo"
            className={styles.logo}
          />
        )}
      </div>

      {!isExpanded && (
        <button 
          className={styles.collapsedNewChatButton}
          onClick={onNewConversation}
          title="Nova Conversa"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path 
              d="M12 5v14m-7-7h14" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </svg>
        </button>
      )}

      {isExpanded && (
        <div className={styles.sidebarContent}>
          <button className={styles.newChatButton} onClick={onNewConversation}>
            <svg className={styles.newChatIcon} viewBox="0 0 24 24" fill="none">
              <path 
                d="M12 5v14m-7-7h14" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
            Nova Conversa
          </button>
          
          {conversations.length > 0 && (
            <>
              <h3 className={styles.sidebarTitle} onClick={() => setConversationsExpanded(!conversationsExpanded)}>
                Conversas Recentes
                <FontAwesomeIcon icon={conversationsExpanded ? faChevronDown : faChevronRight} />
              </h3>
              {conversationsExpanded && (
                <div className={styles.conversationsContainer}>
                  {conversations.map((conv) => (
                    <div
                      key={conv.id}
                      className={`${styles.conversationItem} ${conv.id === currentConversationId ? styles.active : ''}`}
                      onClick={() => onLoadConversation(conv.id)}
                    >
                      <span className={styles.conversationTitle}>{conv.title}</span>
                      <button
                        className={styles.deleteButton}
                        onClick={(e) => handleDeleteConversation(e, conv.id)}
                        title="Excluir conversa"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
          
          {suggestedLinks.length > 0 && (
            <>
              <h3 className={styles.sidebarTitle} onClick={() => setLinksExpanded(!linksExpanded)}>
                Recursos sugeridos
                <FontAwesomeIcon icon={linksExpanded ? faChevronDown : faChevronRight} />
              </h3>
              {linksExpanded && (
                <div className={styles.linksContainer}>
                  {suggestedLinks.map((link, index) => (
                    <a
                      key={index}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.suggestedLink}
                    >
                      <div className={styles.linkContent}>
                        <span className={styles.linkTitle}>
                          {link.title || link.slug}
                        </span>
                      </div>
                      <ExternalLinkIcon />
                    </a>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Sidebar;
