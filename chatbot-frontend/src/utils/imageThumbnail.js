const THUMBNAIL_STORAGE_KEY = 'chatbot_image_thumbnails';
const MAX_THUMBNAIL_SIZE = 150;

export const createImageThumbnail = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > MAX_THUMBNAIL_SIZE) {
            height *= MAX_THUMBNAIL_SIZE / width;
            width = MAX_THUMBNAIL_SIZE;
          }
        } else {
          if (height > MAX_THUMBNAIL_SIZE) {
            width *= MAX_THUMBNAIL_SIZE / height;
            height = MAX_THUMBNAIL_SIZE;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        resolve(canvas.toDataURL('image/jpeg', 0.7));
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
};

export const createVideoThumbnail = (file) => {
  return new Promise((resolve) => {
    const video = document.createElement('video');
    video.preload = 'metadata';
    video.muted = true;
    
    video.onloadeddata = () => {
      video.currentTime = 1;
    };
    
    video.onseeked = () => {
      const canvas = document.createElement('canvas');
      let width = video.videoWidth;
      let height = video.videoHeight;

      if (width > height) {
        if (width > MAX_THUMBNAIL_SIZE) {
          height *= MAX_THUMBNAIL_SIZE / width;
          width = MAX_THUMBNAIL_SIZE;
        }
      } else {
        if (height > MAX_THUMBNAIL_SIZE) {
          width *= MAX_THUMBNAIL_SIZE / height;
          height = MAX_THUMBNAIL_SIZE;
        }
      }

      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, width, height);
      
      resolve(canvas.toDataURL('image/jpeg', 0.7));
      URL.revokeObjectURL(video.src);
    };
    
    video.src = URL.createObjectURL(file);
  });
};

export const saveThumbnail = (fileId, thumbnailData) => {
  const thumbnails = JSON.parse(localStorage.getItem(THUMBNAIL_STORAGE_KEY) || '{}');
  thumbnails[fileId] = thumbnailData;
  localStorage.setItem(THUMBNAIL_STORAGE_KEY, JSON.stringify(thumbnails));
};

export const getThumbnail = (fileId) => {
  const thumbnails = JSON.parse(localStorage.getItem(THUMBNAIL_STORAGE_KEY) || '{}');
  return thumbnails[fileId];
};
