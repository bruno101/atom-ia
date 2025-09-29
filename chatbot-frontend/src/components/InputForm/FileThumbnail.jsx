import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilePdf, faFileAudio, faFileVideo, faTimes } from '@fortawesome/free-solid-svg-icons';
import styles from './FileThumbnail.module.css';

/**
 * Componente para exibir miniatura de arquivo no campo de input
 */
const FileThumbnail = ({ file, onRemove }) => {
  // Determina o ícone baseado no tipo de arquivo
  const getFileIcon = (file) => {
    const fileName = file.name.toLowerCase();
    const fileType = file.type.toLowerCase();
    
    if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
      return faFilePdf;
    } else if (fileType.startsWith('audio/') || fileName.endsWith('.mp3')) {
      return faFileAudio;
    } else if (fileType.startsWith('video/') || fileName.endsWith('.mp4')) {
      return faFileVideo;
    }
    return faFilePdf; // fallback
  };

  // Determina a cor baseada no tipo de arquivo
  const getFileColor = (file) => {
    const fileName = file.name.toLowerCase();
    const fileType = file.type.toLowerCase();
    
    if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
      return '#dc3545'; // vermelho para PDF
    } else if (fileType.startsWith('audio/') || fileName.endsWith('.mp3')) {
      return '#28a745'; // verde para áudio
    } else if (fileType.startsWith('video/') || fileName.endsWith('.mp4')) {
      return '#007bff'; // azul para vídeo
    }
    return '#6c757d'; // cinza padrão
  };

  return (
    <div className={styles.thumbnail}>
      <div className={styles.fileIcon} style={{ color: getFileColor(file) }}>
        <FontAwesomeIcon icon={getFileIcon(file)} />
      </div>
      <span className={styles.fileName}>{file.name}</span>
      <button
        type="button"
        onClick={onRemove}
        className={styles.removeButton}
        title="Remover arquivo"
      >
        <FontAwesomeIcon icon={faTimes} />
      </button>
    </div>
  );
};

export default FileThumbnail;