const formatosTexto = process.env.REACT_APP_FORMATOS_SUPORTADOS_TEXTO?.split(',') || [];
const formatosAudio = process.env.REACT_APP_FORMATOS_SUPORTADOS_AUDIO?.split(',') || [];
const formatosVideo = process.env.REACT_APP_FORMATOS_SUPORTADOS_VIDEO?.split(',') || [];
const formatosImagem = process.env.REACT_APP_FORMATOS_SUPORTADOS_IMAGEM?.split(',') || [];

const sendToBackend = async (file, endpoint) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(endpoint, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Erro ao processar arquivo: ${response.statusText}`);
  }
  
  return await response.json();
};

export const processPDF = (file) => sendToBackend(file, process.env.REACT_APP_API_PROCESSAMENTO_PDF);
export const processAudio = (file) => sendToBackend(file, 'http://localhost:8000/process-audio');
export const processImage = (file) => sendToBackend(file, 'http://localhost:8000/process-image');
export const processVideo = (file) => sendToBackend(file, 'http://localhost:8000/process-video');

/**
 * Processa URL de página web
 * @param {string} url - URL da página web
 * @returns {Promise<Object>} - JSON estruturado para consulta
 */
export const processURL = async (url) => {
  console.log('\n🔄 Iniciando processamento da URL:', url);
  
  // Barra de progresso
  const progress = {
    current: 0,
    total: 4,
    update(step, message) {
      this.current = step;
      const percent = Math.round((this.current / this.total) * 100);
      const bar = '█'.repeat(Math.floor(percent / 5)) + '░'.repeat(20 - Math.floor(percent / 5));
      console.log(`📊 [${bar}] ${percent}% - ${message}`);
    }
  };
  
  try {
    progress.update(1, 'Enviando URL para processamento...');
    
    const response = await fetch('http://localhost:8000/process-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url })
    });
    
    progress.update(2, 'Recebendo resposta do servidor...');
    
    if (!response.ok) {
      throw new Error(`Erro ao processar URL: ${response.statusText}`);
    }
    
    progress.update(3, 'Processando dados com LLM...');
    
    const result = await response.json();
    
    progress.update(4, 'Processamento concluído!');
    
    console.log('✅ URL processada com sucesso\n');
    console.log('Query estruturada:', result);
    
    return result;
    
  } catch (error) {
    console.error('❌ Erro ao processar URL:', error.message);
    throw error;
  }
};

export const processFile = async (file) => {
  const fileName = file.name.toLowerCase();
  const fileType = file.type.toLowerCase();

  if (fileType === 'application/pdf' || formatosTexto.some(ext => fileName.endsWith(ext))) {
    return await processPDF(file);
  } else if (fileType.startsWith('audio/') || formatosAudio.some(ext => fileName.endsWith(ext))) {
    return await processAudio(file);
  } else if (fileType.startsWith('video/') || formatosVideo.some(ext => fileName.endsWith(ext))) {
    return await processVideo(file);
  } else if (fileType.startsWith('image/') || formatosImagem.some(ext => fileName.endsWith(ext))) {
    return await processImage(file);
  } else {
    throw new Error(`Formato de arquivo não suportado: ${fileType || 'desconhecido'}`);
  }
};