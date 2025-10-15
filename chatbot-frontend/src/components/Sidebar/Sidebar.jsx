import { useState } from "react";
import ExternalLinkIcon from "../../icons/ExternalLinkIcon";
import styles from './Sidebar.module.css';

const Sidebar = ({ suggestedLinks }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isPinned, setIsPinned] = useState(false);

  const isExpanded = isHovered || isPinned;

  const handleTogglePin = () => {
    setIsPinned(!isPinned);
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

      {isExpanded && (
        <div className={styles.sidebarContent}>
          <button className={styles.newChatButton} onClick={() => window.location.reload()}>
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
          
          {suggestedLinks.length > 0 && (
            <h3 className={styles.sidebarTitle}>Recursos sugeridos</h3>
          )}
          
          {suggestedLinks.length > 0 ? (
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
          ) : (
            <div className={styles.noLinks}>
              <p>Faça uma consulta para ver recursos relacionados</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Sidebar;
