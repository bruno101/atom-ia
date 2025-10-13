import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilePdf, faFileAudio, faFileVideo, faFileImage, faTimes } from '@fortawesome/free-solid-svg-icons';
import styles from './FileThumbnail.module.css';

const formatosTexto = process.env.REACT_APP_FORMATOS_SUPORTADOS_TEXTO?.split(',') || [];
const formatosAudio = process.env.REACT_APP_FORMATOS_SUPORTADOS_AUDIO?.split(',') || [];
const formatosVideo = process.env.REACT_APP_FORMATOS_SUPORTADOS_VIDEO?.split(',') || [];
const formatosImagem = process.env.REACT_APP_FORMATOS_SUPORTADOS_IMAGEM?.split(',') || [];

/**
 * Componente para exibir miniatura de arquivo no campo de input
 */
const FileThumbnail = ({ file, onRemove, variant = 'input' }) => {
  // Determina o ícone baseado no tipo de arquivo
  const getFileIcon = (file) => {
    const fileName = file.name.toLowerCase();
    const fileType = file.type.toLowerCase();
    
    if (fileType.startsWith('image/') || formatosImagem.some(ext => fileName.endsWith(ext))) {
      return faFileImage;
    } else if (fileType.startsWith('video/') || formatosVideo.some(ext => fileName.endsWith(ext))) {
      return faFileVideo;
    } else if (fileType.startsWith('audio/') || formatosAudio.some(ext => fileName.endsWith(ext))) {
      return faFileAudio;
    } else if (fileType === 'application/pdf' || formatosTexto.some(ext => fileName.endsWith(ext))) {
      return faFilePdf;
    }
    return faFilePdf; // fallback
  };

  // Determina a cor baseada no tipo de arquivo
  const getFileColor = (file) => {
    const fileName = file.name.toLowerCase();
    const fileType = file.type.toLowerCase();
    
    if (fileType.startsWith('image/') || formatosImagem.some(ext => fileName.endsWith(ext))) {
      return '#ffc107'; // amarelo para imagem
    } else if (fileType.startsWith('video/') || formatosVideo.some(ext => fileName.endsWith(ext))) {
      return '#007bff'; // azul para vídeo
    } else if (fileType.startsWith('audio/') || formatosAudio.some(ext => fileName.endsWith(ext))) {
      return '#28a745'; // verde para áudio
    } else if (fileType === 'application/pdf' || formatosTexto.some(ext => fileName.endsWith(ext))) {
      return '#dc3545'; // vermelho para PDF
    }
    return '#6c757d'; // cinza padrão
  };

  return (
    <div className={`${styles.thumbnail} ${variant === 'message' ? styles.thumbnailMessage : styles.thumbnailInput}`}>
      <div className={styles.fileIcon} style={{ color: getFileColor(file) }}>
        <FontAwesomeIcon icon={getFileIcon(file)} />
      </div>
      <span className={styles.fileName}>{file.name}</span>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className={styles.removeButton}
          title="Remover arquivo"
        >
          <FontAwesomeIcon icon={faTimes} />
        </button>
      )}
    </div>
  );
};

export default FileThumbnail;