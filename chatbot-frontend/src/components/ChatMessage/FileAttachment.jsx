import FileThumbnail from '../InputForm/FileThumbnail';

const FileAttachment = ({ fileMetadata }) => {
  const file = {
    name: fileMetadata.nome_arquivo,
    type: fileMetadata.tipo === 'pdf' ? 'application/pdf' :
          fileMetadata.tipo === 'audio' ? 'audio/mp3' :
          fileMetadata.tipo === 'video' ? 'video/mp4' : 'application/pdf'
  };

  return <FileThumbnail file={file} variant="message" />;
};

export default FileAttachment;
