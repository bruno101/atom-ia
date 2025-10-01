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
  
  const response = await fetch('http://localhost:8000/process-pdf', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Erro ao processar PDF: ${response.statusText}`);
  }
  
  const result = await response.json();
  return result.query;
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
 * Processa arquivos de áudio MP3
 * @param {File} file - Arquivo MP3
 * @returns {Promise<string>} - Texto transcrito ou consulta gerada
 */
export const processMP3 = async (file) => {
  // TODO: Implementar transcrição de áudio
  console.log('Processando MP3:', file.name);
  return "Pesquise sobre beija-flores";
};

/**
 * Processa arquivos de vídeo MP4
 * @param {File} file - Arquivo MP4
 * @returns {Promise<string>} - Texto transcrito ou consulta gerada
 */
export const processMP4 = async (file) => {
  // TODO: Implementar transcrição de vídeo
  console.log('Processando MP4:', file.name);
  return "Pesquise sobre beija-flores";
};

/**
 * Processa arquivo baseado no tipo
 * @param {File} file - Arquivo a ser processado
 * @returns {Promise<string>} - Resultado do processamento
 */
export const processFile = async (file) => {
  const fileType = file.type.toLowerCase();
  const fileName = file.name.toLowerCase();

  if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
    return await processPDF(file);
  } else if (fileType === 'audio/mp3' || fileType === 'audio/mpeg' || fileName.endsWith('.mp3')) {
    return await processMP3(file);
  } else if (fileType === 'video/mp4' || fileName.endsWith('.mp4')) {
    return await processMP4(file);
  } else {
    throw new Error(`Formato de arquivo não suportado: ${fileType || 'desconhecido'}`);
  }
};