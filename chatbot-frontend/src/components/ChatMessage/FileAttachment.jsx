import { getThumbnail } from '../../utils/imageThumbnail';
import FileThumbnail from '../InputForm/FileThumbnail';
import styles from './FileAttachment.module.css';

const FileAttachment = ({ fileMetadata, messageId }) => {
  const thumbnail = getThumbnail(messageId);
  
  if ((fileMetadata.tipo === 'image' || fileMetadata.tipo === 'video') && thumbnail) {
    return (
      <div className={styles.imageThumbnail}>
        <img src={thumbnail} alt={fileMetadata.nome_arquivo} />
        <div className={styles.imageName}>{fileMetadata.nome_arquivo}</div>
      </div>
    );
  }
  
  const file = {
    name: fileMetadata.nome_arquivo,
    type: fileMetadata.tipo === 'pdf' ? 'application/pdf' :
          fileMetadata.tipo === 'audio' ? 'audio/mp3' :
          fileMetadata.tipo === 'video' ? 'video/mp4' : 'application/pdf'
  };

  return <FileThumbnail file={file} variant="message" />;
};

export default FileAttachment;
