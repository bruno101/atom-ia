export const formatosTexto = process.env.REACT_APP_FORMATOS_SUPORTADOS_TEXTO?.split(',') || [];
export const formatosAudio = process.env.REACT_APP_FORMATOS_SUPORTADOS_AUDIO?.split(',') || [];
export const formatosVideo = process.env.REACT_APP_FORMATOS_SUPORTADOS_VIDEO?.split(',') || [];
export const formatosImagem = process.env.REACT_APP_FORMATOS_SUPORTADOS_IMAGEM?.split(',') || [];

const sendToBackend = async (file, endpoint) => {
  console.log('📤 Enviando arquivo:', {
    arquivo: file.name,
    tipo: file.type,
    tamanho: file.size,
    endpoint
  });
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData
    });
    
    console.log('📥 Resposta recebida:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Erro na resposta:', errorText);
      throw new Error(`Erro ${response.status}: ${errorText || response.statusText}`);
    }
    
    const result = await response.json();
    console.log('✅ Processamento concluído:', result);
    return result;
  } catch (error) {
    console.error('💥 Erro na requisição:', error);
    throw error;
  }
};

export const processPDF = (file) => sendToBackend(file, process.env.REACT_APP_API_PROCESSAMENTO_PDF);
export const processAudio = (file) => sendToBackend(file, process.env.REACT_APP_API_PROCESSAMENTO_AUDIO);
export const processImage = (file) => sendToBackend(file, process.env.REACT_APP_API_PROCESSAMENTO_IMAGEM);
export const processVideo = (file) => sendToBackend(file, process.env.REACT_APP_API_PROCESSAMENTO_VIDEO);

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
    
    const response = await fetch(process.env.REACT_APP_API_PROCESSAMENTO_URL, {
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

export const transcribeAudio = async (file) => {
  console.log('🎤 Iniciando transcrição de áudio:', file.name);
  
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(process.env.REACT_APP_API_TRANSCRICAO_AUDIO, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Erro ao transcrever: ${response.statusText}`);
  }
  
  const result = await response.json();
  console.log('✅ Transcrição concluída');
  return result.transcription;
};

export const transcribeVideo = async (file) => {
  console.log('🎬 Iniciando transcrição de vídeo:', file.name);
  
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(process.env.REACT_APP_API_TRANSCRICAO_VIDEO, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Erro ao transcrever: ${response.statusText}`);
  }
  
  const result = await response.json();
  console.log('✅ Transcrição concluída');
  return result.transcription;
};

export const transcribeFile = async (file) => {
  const fileName = file.name.toLowerCase();
  const fileType = file.type.toLowerCase();

  if (fileType.startsWith('video/') || formatosVideo.some(ext => fileName.endsWith(ext))) {
    return await transcribeVideo(file);
  } else if (fileType.startsWith('audio/') || formatosAudio.some(ext => fileName.endsWith(ext))) {
    return await transcribeAudio(file);
  } else {
    throw new Error('Arquivo não é áudio ou vídeo');
  }
};

export const getTranscribeEndpoint = (file) => {
  const fileName = file.name.toLowerCase();
  const fileType = file.type.toLowerCase();

  if (fileType.startsWith('video/') || formatosVideo.some(ext => fileName.endsWith(ext))) {
    return process.env.REACT_APP_API_TRANSCRICAO_VIDEO;
  } else if (fileType.startsWith('audio/') || formatosAudio.some(ext => fileName.endsWith(ext))) {
    return process.env.REACT_APP_API_TRANSCRICAO_AUDIO;
  } else {
    throw new Error('Arquivo não é áudio ou vídeo');
  }
};

export const isAudioOrVideoFile = (file) => {
  if (!file) return false;
  const fileName = file.name.toLowerCase();
  const fileType = file.type.toLowerCase();
  
  return fileType.startsWith('audio/') || fileType.startsWith('video/') ||
         formatosAudio.some(ext => fileName.endsWith(ext)) ||
         formatosVideo.some(ext => fileName.endsWith(ext));
};

export const processFile = async (file) => {
  const fileName = file.name.toLowerCase();
  const fileType = file.type.toLowerCase();

  console.log('🔍 Processando arquivo:', {
    nome: file.name,
    tipo: fileType,
    tamanho: file.size,
    formatosTexto,
    formatosAudio,
    formatosVideo,
    formatosImagem
  });

  if (fileType === 'application/pdf' || formatosTexto.some(ext => fileName.endsWith(ext))) {
    console.log('📄 Detectado como PDF');
    return await processPDF(file);
  } else if (fileType.startsWith('image/') || formatosImagem.some(ext => fileName.endsWith(ext))) {
    console.log('🖼️ Detectado como IMAGEM');
    return await processImage(file);
  } else if (fileType.startsWith('video/')) {
    console.log('🎬 Detectado como VÍDEO (MIME type)');
    return await processVideo(file);
  } else if (fileType.startsWith('audio/')) {
    console.log('🎵 Detectado como ÁUDIO (MIME type)');
    return await processAudio(file);
  } else if (fileName.endsWith('.mp4')) {
    console.log('🎬 .mp4 sem MIME type - assumindo VÍDEO');
    return await processVideo(file);
  } else if (formatosVideo.some(ext => fileName.endsWith(ext))) {
    console.log('🎬 Detectado como VÍDEO (extensão)');
    return await processVideo(file);
  } else if (formatosAudio.some(ext => fileName.endsWith(ext))) {
    console.log('🎵 Detectado como ÁUDIO (extensão)');
    return await processAudio(file);
  } else {
    console.error('❌ Formato não suportado:', fileType);
    throw new Error(`Formato de arquivo não suportado: ${fileType || 'desconhecido'}`);
  }
};