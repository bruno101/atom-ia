/**
 * Processador de arquivos para diferentes formatos
 * Cada formato tem seu método específico de processamento
 */


/**
 * Envia arquivo PDF para processamento no backend
 * @param {File} file - Arquivo PDF
 * @returns {Promise<string>} - Query gerada pelo backend
 */
const processPDFBackend = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(process.env.REACT_APP_API_PROCESSAMENTO_PDF, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Erro ao processar PDF: ${response.statusText}`);
  }
  
  const result = await response.json();
  return result;
};

/**
 * Processa arquivos PDF
 * @param {File} file - Arquivo PDF
 * @returns {Promise<string>} - Query gerada pelo backend
 */
export const processPDF = async (file) => {
  console.log('\n🔄 Iniciando processamento do PDF:', file.name);
  
  try {
    // Verifica se é um arquivo PDF válido
    if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
      throw new Error('Arquivo deve ser um PDF válido');
    }
    
    // Envia arquivo para processamento no backend
    const query = await processPDFBackend(file);
    
    console.log('✅ PDF processado com sucesso\n');
    console.log('Query gerada:', query);
    
    // Retorna a query gerada pelo backend
    return query;
    
  } catch (error) {
    console.error('❌ Erro ao processar PDF:', error.message);
    throw error;
  }
};

/**
 * Envia arquivo de áudio para processamento no backend
 * @param {File} file - Arquivo de áudio
 * @returns {Promise<Object>} - Query gerada pelo backend
 */
const processAudioBackend = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/process-audio', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Erro ao processar áudio: ${response.statusText}`);
  }
  
  const result = await response.json();
  return result;
};

/**
 * Processa arquivos de áudio (MP3, MP4, M4A)
 * @param {File} file - Arquivo de áudio
 * @returns {Promise<Object>} - Query gerada pelo backend
 */
export const processAudio = async (file) => {
  console.log('\n🔄 Iniciando processamento do áudio:', file.name);
  
  try {
    // Verifica se é um arquivo de áudio válido
    const validTypes = ['audio/mp3', 'audio/mpeg', 'audio/mp4', 'video/mp4'];
    const validExtensions = ['.mp3', '.mp4', '.m4a'];
    const fileName = file.name.toLowerCase();
    
    if (!validTypes.includes(file.type) && !validExtensions.some(ext => fileName.endsWith(ext))) {
      throw new Error('Arquivo deve ser um áudio válido (MP3, MP4 ou M4A)');
    }
    
    // Envia arquivo para processamento no backend
    const query = await processAudioBackend(file);
    
    console.log('✅ Áudio processado com sucesso\n');
    console.log('Query gerada:', query);
    
    // Retorna a query gerada pelo backend
    return query;
    
  } catch (error) {
    console.error('❌ Erro ao processar áudio:', error.message);
    throw error;
  }
};

/**
 * Envia arquivo de imagem para processamento no backend
 * @param {File} file - Arquivo de imagem
 * @returns {Promise<Object>} - Query gerada pelo backend
 */
const processImageBackend = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/process-image', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Erro ao processar imagem: ${response.statusText}`);
  }
  
  const result = await response.json();
  return result;
};

/**
 * Processa arquivos de imagem (JPG, PNG, WEBP)
 * @param {File} file - Arquivo de imagem
 * @returns {Promise<Object>} - Query gerada pelo backend
 */
export const processImage = async (file) => {
  console.log('\n🔄 Iniciando processamento da imagem:', file.name);
  
  try {
    // Verifica se é um arquivo de imagem válido
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const validExtensions = ['.jpg', '.jpeg', '.png', '.webp'];
    const fileName = file.name.toLowerCase();
    
    if (!validTypes.includes(file.type) && !validExtensions.some(ext => fileName.endsWith(ext))) {
      throw new Error('Arquivo deve ser uma imagem válida (JPG, PNG ou WEBP)');
    }
    
    // Envia arquivo para processamento no backend
    const query = await processImageBackend(file);
    
    console.log('✅ Imagem processada com sucesso\n');
    console.log('Query gerada:', query);
    
    // Retorna a query gerada pelo backend
    return query;
    
  } catch (error) {
    console.error('❌ Erro ao processar imagem:', error.message);
    throw error;
  }
};

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

/**
 * Processa arquivo baseado no tipo
 * @param {File} file - Arquivo a ser processado
 * @returns {Promise<string>} - Resultado do processamento
 */
export const processFile = async (file) => {
  const fileType = file.type.toLowerCase();
  const fileName = file.name.toLowerCase();
  console.log(fileName, fileType)

  if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
    return await processPDF(file);
  } else if (fileType === 'audio/mp3' || fileType === 'audio/mpeg' || fileType === 'audio/mp4' || 
             fileName.endsWith('.mp3') || fileName.endsWith('.mp4') || fileName.endsWith('.m4a')) {
    return await processAudio(file);
  } else if (fileType === 'image/jpeg' || fileType === 'image/jpg' || fileType === 'image/png' || fileType === 'image/webp' ||
             fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') || fileName.endsWith('.png') || fileName.endsWith('.webp')) {
    return await processImage(file);
  } else {
    throw new Error(`Formato de arquivo não suportado: ${fileType || 'desconhecido'}`);
  }
};