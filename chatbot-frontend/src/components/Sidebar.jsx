import { useState } from "react";
import ExternalLinkIcon from "./icons/ExternalLinkIcon";

const Sidebar = ({ showSidebar, toggleSidebar, suggestedLinks }) => {

  return (
    <>
      <div className="mobile-header">
        <button className="sidebar-toggle" onClick={toggleSidebar}>
          <span>Recursos sugeridos</span>
        </button>
      </div>
      <div className={`sidebar ${showSidebar ? "sidebar-visible" : ""}`}>
        <div className="sidebar-section">
          <h3 className="sidebar-title">Recursos sugeridos:</h3>
          <button className="close-sidebar" onClick={toggleSidebar}>
            &times;
          </button>

          {suggestedLinks.length > 0 ? (
            <div className="links-container">
              {suggestedLinks.map((link, index) => (
                <a
                  key={index}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="suggested-link"
                >
                  <div className="link-content">
                    <span className="link-title">
                      {link.title || link.slug}
                    </span>
                    {link.description && (
                      <span className="link-description">{link.descricao}</span>
                    )}
                  </div>
                  <ExternalLinkIcon />
                </a>
              ))}
            </div>
          ) : (
            <div className="no-links">
              <p>Faça uma consulta para ver recursos relacionados</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
