import ExternalLinkIcon from "../../icons/ExternalLinkIcon";
import styles from './Sidebar.module.css';

const Sidebar = ({ showSidebar, toggleSidebar, suggestedLinks }) => {
  return (
    <>
      <div className={styles.mobileHeader}>
        <button className={styles.sidebarToggle} onClick={toggleSidebar}>
          <span>Recursos sugeridos</span>
        </button>
      </div>

      <div className={`${styles.sidebar} ${showSidebar ? styles.sidebarVisible : ""}`}>
        <div className={styles.sidebarSection}>
        <img
        src="/images/an-logo.webp"
        alt=""
        className={styles.logo}
      />
          <h3 className={styles.sidebarTitle}>Recursos sugeridos:</h3>
          <button className={styles.closeSidebar} onClick={toggleSidebar}>
            &times;
          </button>

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
      </div>
    </>
  );
};

export default Sidebar;
