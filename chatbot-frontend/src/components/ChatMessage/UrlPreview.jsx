import { useState, useEffect } from 'react';
import styles from './UrlPreview.module.css';

const UrlPreview = ({ url }) => {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);

  const getYouTubeId = (url) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)/);
    return match ? match[1] : null;
  };

  const youtubeId = getYouTubeId(url);

  useEffect(() => {
    if (youtubeId) {
      setLoading(false);
      return;
    }

    const fetchPreview = async () => {
      try {
        const response = await fetch(`https://api.microlink.io/?url=${encodeURIComponent(url)}`);
        const data = await response.json();
        if (data.status === 'success' && data.data) {
          setPreview(data.data);
        }
      } catch (error) {
        console.error('Error fetching URL preview:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPreview();
  }, [url, youtubeId]);

  if (loading) return null;

  if (youtubeId) {
    return (
      <div className={styles.urlPreview}>
        <iframe
          className={styles.youtubeEmbed}
          src={`https://www.youtube.com/embed/${youtubeId}`}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    );
  }

  if (!preview) return null;

  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className={styles.urlPreview}>
      {preview.image?.url && (
        <img src={preview.image.url} alt={preview.title || 'Preview'} className={styles.previewImage} />
      )}
      <div className={styles.previewContent}>
        {preview.title && <div className={styles.previewTitle}>{preview.title}</div>}
        {preview.description && (
          <div className={styles.previewDescription}>{preview.description}</div>
        )}
        <div className={styles.previewUrl}>{preview.url || url}</div>
      </div>
    </a>
  );
};

export default UrlPreview;
