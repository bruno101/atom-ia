/**
 * Processador de arquivos para diferentes formatos
 * Cada formato tem seu método específico de processamento
 */
import * as pdfjsLib from 'pdfjs-dist';

// Configuração do PDF.js com worker inline
// Configuração simples do worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

/**
 * Exibe barra de progresso no console
 * @param {number} current - Progresso atual
 * @param {number} total - Total de etapas
 * @param {string} step - Nome da etapa atual
 */
const showProgress = (current, total, step) => {
  const percentage = Math.round((current / total) * 100);
  const bar = '█'.repeat(Math.floor(percentage / 5)) + '░'.repeat(20 - Math.floor(percentage / 5));
  console.log(`\r[${bar}] ${percentage}% - ${step}`);
};

/**
 * Extrai texto do arquivo PDF
 * @param {File} file - Arquivo PDF
 * @returns {Promise<string>} - Texto extraído
 */
const extractTextFromPDF = async (file) => {
  showProgress(1, 6, 'Carregando PDF...');
  
  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
  
  showProgress(2, 6, 'Extraindo texto das páginas...');
  
  let fullText = '';
  const numPages = pdf.numPages;
  
  for (let i = 1; i <= numPages; i++) {
    const page = await pdf.getPage(i);
    const textContent = await page.getTextContent();
    const pageText = textContent.items.map(item => item.str).join(' ');
    fullText += pageText + '\n';
  }
  
  if (fullText.trim().length < 50) {
    throw new Error('O arquivo PDF contém apenas imagens. Por favor, anexe um arquivo que contenha texto.');
  }
  
  return fullText;
};

/**
 * Cria resumo do texto extraído
 * @param {string} text - Texto completo
 * @returns {string} - Resumo do texto
 */
const createSummary = (text) => {
  showProgress(3, 6, 'Criando resumo...');
  
  // Limita o texto para criar um resumo
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 20);
  const summary = sentences.slice(0, 5).join('. ') + '.';
  
  return summary || text.substring(0, 500) + '...';
};

/**
 * Extrai informações estruturadas do texto
 * @param {string} text - Texto do PDF
 * @returns {Object} - Informações extraídas
 */
const extractInformation = (text) => {
  showProgress(4, 6, 'Extraindo informações...');
  
  // Extração básica de informações (pode ser melhorada com NLP)
  const lines = text.split('\n').filter(line => line.trim());
  
  // Tenta identificar título (primeira linha significativa)
  const titulo = lines.find(line => line.length > 10 && line.length < 100) || 'Documento sem título';
  
  // Busca por padrões de autor
  const autorMatch = text.match(/(?:autor|author|by)\s*:?\s*([^\n]{5,50})/i);
  const autor = autorMatch ? autorMatch[1].trim() : 'Autor não identificado';
  
  // Identifica assunto (palavras mais frequentes)
  const words = text.toLowerCase().match(/\b\w{4,}\b/g) || [];
  const wordCount = {};
  words.forEach(word => wordCount[word] = (wordCount[word] || 0) + 1);
  const topWords = Object.entries(wordCount)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 3)
    .map(([word]) => word);
  
  const assunto = topWords.join(', ') || 'Assunto não identificado';
  
  // Palavras-chave (palavras relevantes)
  const palavrasChave = topWords.slice(0, 5).join(', ');
  
  // Busca por referências
  const referenciaMatch = text.match(/(?:referência|reference|bibliografia)([\s\S]{0,200})/i);
  const referencias = referenciaMatch ? referenciaMatch[1].trim() : 'Referências não encontradas';
  
  return { titulo, autor, assunto, palavrasChave, referencias };
};

/**
 * Gera query de busca baseada nas informações extraídas
 * @param {Object} info - Informações extraídas
 * @param {string} resumo - Resumo do documento
 * @returns {string} - Query gerada
 */
const generateSearchQuery = (info, resumo) => {
  showProgress(5, 6, 'Gerando query de busca...');
  
  const { titulo, autor, assunto, palavrasChave, referencias } = info;
  
  const query = `Procure informações sobre "${titulo}" de autoria de "${autor}" que tratem do assunto "${assunto}" ou tenham relação com "${palavrasChave}" e "${referencias}" ou qualquer informação relevante contidas nesse resumo "${resumo}".`;
  
  // Exibe query no console
  console.log('\n=== QUERY GERADA ===');
  console.log('Query:', query);
  console.log('====================\n');
  
  return query;
};

/**
 * Processa arquivos PDF
 * @param {File} file - Arquivo PDF
 * @returns {Promise<string>} - Mensagem para o input
 */
export const processPDF = async (file) => {
  console.log('\n🔄 Iniciando processamento do PDF:', file.name);
  
  try {
    // Etapa 1: Extrair texto
    const text = await extractTextFromPDF(file);
    
    // Etapa 2: Criar resumo
    const resumo = createSummary(text);
    
    // Etapa 3: Extrair informações
    const info = extractInformation(text);
    
    // Etapa 4: Gerar query
    const query = generateSearchQuery(info, resumo);
    
    showProgress(6, 6, 'Processamento concluído!');
    console.log('✅ PDF processado com sucesso\n');
    
    // Retorna a query gerada para o input
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