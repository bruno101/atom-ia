# 🤖 SIAN - Sistema de Informações do Arquivo Nacional

Uma interface moderna e intuitiva para consultas arquivísticas inteligentes, conectada ao banco de dados Oracle.

## ✨ Características
 
- 🔍 **Busca Inteligente**: IA especializada em consultas arquivísticas
- 🎤 **Busca por Voz**: Reconhecimento de voz para consultas faladas
- 🔊 **Leitura em Voz Alta**: Síntese de voz para respostas do chatbot
- 📎 **Upload de Arquivos**: Anexe PDF, MP3 e MP4 com drag & drop
- 💬 **Interface de Chat**: Conversação natural com o sistema
- 📱 **Design Responsivo**: Funciona em desktop e mobile
- 🔗 **Links Sugeridos**: Recursos relacionados exibidos dinamicamente
- ⚡ **Streaming em Tempo Real**: Respostas progressivas para melhor UX
 
## 🚀 Tecnologias

### Frontend
- **React 18** - Framework principal
- **Create React App** - Build tool e dev server
- **CSS Modules** - Estilização modular
- **Design System Gov.br** - Componentes governamentais
- **Web Speech API** - Reconhecimento de voz e síntese de voz nativos do navegador

### Backend & IA
- **Modelo LLM**: Google Gemini 2.5 Flash - Geração de respostas e processamento de linguagem natural
- **Oracle Database** - Banco de dados principal para armazenamento de documentos
- **Elasticsearch** - Motor de busca para consultas textuais e indexação
- **FastAPI** - Framework web para APIs REST

## 📦 Instalação
 
```bash
# Clone o repositório
git clone [url-do-repositorio]
 
# Entre no diretório
cd chatbot-frontend
 
# Instale as dependências
npm install
 
# Inicie o servidor de desenvolvimento
npm start
```
 
## 🛠️ Scripts Disponíveis
 
```bash
npm start            # Servidor de desenvolvimento
npm run build        # Build para produção
npm test             # Executar testes
npm run eject        # Ejetar configuração CRA
```
 
## 🏗️ Estrutura do Projeto

### Frontend
```
src/
├── components/          # Componentes React
│   ├── Header/         # Cabeçalho governamental da aplicação
│   ├── ChatHeader/     # Cabeçalho do chat com logo NISA
│   ├── ChatMessage/    # Componente de mensagem individual
│   │   ├── ChatMessage.jsx
│   │   ├── UrlPreview.jsx  # Preview de URLs com YouTube embed
│   │   └── FileAttachment.jsx  # Exibição de arquivos anexados
│   ├── MessageList/    # Lista de mensagens com scroll
│   ├── InputForm/      # Formulário com voz, upload e transcrição
│   │   ├── InputForm.jsx
│   │   ├── FileThumbnail.jsx  # Thumbnail de arquivos
│   │   └── TranscriptModal.jsx  # Modal de transcrição
│   ├── Sidebar/        # Barra lateral com histórico e links
│   └── Footer/         # Rodapé institucional
├── features/           # Funcionalidades organizadas
│   └── fileUpload/     # Sistema de upload multimodal
│       ├── FileUploadArea.jsx
│       └── fileProcessor.js  # Processamento de PDF, áudio, vídeo, imagem
├── hooks/              # Hooks personalizados
│   ├── useConversation.js  # Gerenciamento de conversas
│   ├── useSpeechRecognition.js  # Reconhecimento de voz
│   ├── useTextToSpeech.js  # Síntese de voz
│   └── useProgressTimeout.js  # Mensagens de progresso
├── icons/              # Ícones SVG customizados
├── logic/              # Lógica de negócio
│   ├── createHandleSubmit.js  # Lógica de submissão
│   ├── fetchSse.js     # Cliente SSE
│   ├── buildHistorico.js  # Formatação de histórico
│   └── handleTranscribeSSE.js  # Streaming de transcrição
├── utils/              # Utilitários
│   ├── conversationStorage.js  # Persistência local
│   ├── formatTime.js   # Formatação de tempo
│   └── imageThumbnail.js  # Geração de thumbnails
├── config/             # Configurações
│   └── progressConfig.js  # Mensagens de progresso
└── App.jsx            # Componente principal
```

### Backend (python-backend-2)
Veja [python-backend-2/README.md](../python-backend-2/README.md) para documentação completa do backend.

```
python-backend-2/
├── api/                 # Camada de API
│   ├── api_service.py   # Lógica de negócio
│   ├── models.py        # Modelos Pydantic
│   └── routers.py       # Endpoints HTTP
├── processors/          # Processadores multimodais
│   ├── audio_processor.py
│   ├── video_processor.py
│   ├── image_processor.py
│   ├── pdf_processor.py
│   └── url_processor_backend.py
├── rag_models/          # Modelos RAG
│   ├── flash/           # Modelo rápido
│   ├── thinking/        # Modelo avançado
│   └── multimodal/      # Modelo multimodal
├── search_algorithms/   # Algoritmos de busca
├── main.py             # Servidor FastAPI
├── config.py           # Configurações globais
└── requirements.txt    # Dependências Python
```
 
## 🎨 Funcionalidades
 
### Interface Principal
- **Header Governamental**: Design seguindo padrões gov.br
- **Chat Interativo**: Conversação fluida com a IA
- **Sidebar Responsiva**: Links sugeridos com scroll independente
- **Footer Compacto**: Informações institucionais
 
### Experiência do Usuário
- **Scroll Independente**: Chat e sidebar com rolagem separada
- **Input Fixo**: Campo de entrada sempre visível
- **Busca por Voz**: Botão de microfone integrado ao campo de entrada
- **Upload de Arquivos**: Ícone de clipe para anexar PDF, MP3 e MP4
- **Miniaturas de Arquivo**: Preview dos arquivos anexados no campo de input
- **Leitura em Voz Alta**: Botão de áudio em todas as mensagens do chat
- **Feedback Visual**: Indicadores de carregamento e progresso
- **Design Adaptativo**: Layout otimizado para diferentes telas
 
## 🔧 Configuração
 
### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
 
```env
# Endpoints de Chat
REACT_APP_API_URL_FLASH=http://localhost:8000/ask-stream-flash
REACT_APP_API_URL_THINKING=http://localhost:8000/ask-stream
REACT_APP_API_URL_MULTIMODAL=http://localhost:8000/ask-file-stream

# Endpoints de Processamento
REACT_APP_API_PROCESSAMENTO_PDF=http://localhost:8000/process-pdf
REACT_APP_API_PROCESSAMENTO_AUDIO=http://localhost:8000/process-audio
REACT_APP_API_PROCESSAMENTO_VIDEO=http://localhost:8000/process-video
REACT_APP_API_PROCESSAMENTO_IMAGEM=http://localhost:8000/process-image
REACT_APP_API_PROCESSAMENTO_URL=http://localhost:8000/process-url

# Endpoints de Transcrição
REACT_APP_API_TRANSCRICAO_AUDIO=http://localhost:8000/transcribe-audio
REACT_APP_API_TRANSCRICAO_VIDEO=http://localhost:8000/transcribe-video

# Formatos de Arquivo Suportados
REACT_APP_FORMATOS_SUPORTADOS_TEXTO=.pdf
REACT_APP_FORMATOS_SUPORTADOS_AUDIO=.mp3,.wav,.aac,.flac,.m4a,.ogg
REACT_APP_FORMATOS_SUPORTADOS_VIDEO=.mp4,.mov,.mpeg,.mpg,.webm,.avi
REACT_APP_FORMATOS_SUPORTADOS_IMAGEM=.jpeg,.jpg,.png,.webp,.gif,.bmp,.heic,.heif
```

### Arquitetura do Backend
A aplicação utiliza:
- **Google Gemini 2.5 Flash**: Modelo de linguagem para geração de respostas contextuais
- **Oracle Database**: Armazenamento principal dos documentos arquivísticos
- **Elasticsearch**: Índice de busca textual com algoritmos avançados (BM25, TF-IDF)
- **Algoritmos de Busca**: BM25, BM25+, TF-IDF, LambdaMART para recuperação de documentos

### Funcionalidades Avançadas

#### 🎤 Busca por Voz
- **Web Speech API**: Reconhecimento de voz nativo do navegador
- **Idioma**: Configurado para português brasileiro (pt-BR)
- **Interface**: Botão de microfone no estilo WhatsApp
- **Estados visuais**: Animação durante gravação
- **Compatibilidade**: Funciona em navegadores modernos

#### 🔊 Leitura em Voz Alta
- **Speech Synthesis API**: Síntese de voz nativa do navegador
- **Idioma**: Configurado para português brasileiro (pt-BR)
- **Interface**: Botão de áudio em todas as mensagens (usuário e assistente)
- **Limpeza de texto**: Remove formatação Markdown para leitura natural
- **Estados visuais**: Animação durante reprodução
- **Posicionamento**: Canto superior direito para todas as mensagens

#### 📎 Upload de Arquivos
- **Formatos suportados**: PDF, MP3, MP4
- **Drag & Drop**: Arraste arquivos diretamente para o campo de input
- **Ícone de clipe**: Botão dedicado para seleção de arquivos
- **Miniaturas**: Preview dos arquivos com ícones coloridos por tipo
- **Processamento**: Métodos específicos para cada formato de arquivo
- **Interface oculta**: Área de upload aparece apenas quando necessário
- **Remoção fácil**: Botão X para remover arquivos anexados

### Customização
- **Cores**: Modifique as variáveis CSS nos arquivos `.module.css`
- **Layout**: Ajuste breakpoints no `App.css`
- **Componentes**: Personalize componentes individuais
 
## 📱 Responsividade
 
- **Desktop**: Layout completo com sidebar visível
- **Tablet**: Sidebar colapsável
- **Mobile**: Interface otimizada para toque
 
## 🤝 Contribuição
 
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request
 
## 📄 Licença
 
Este projeto está sob a licença [MIT](LICENSE).
 
## 🏛️ Sobre
 
Desenvolvido para o **Arquivo Nacional** como parte do sistema SIAN, facilitando o acesso democrático à informação arquivística através de tecnologia de ponta.
 
---
 
**SIAN** • *Sistema Inteligente de Arquivos Nacionais* • Dataprev © 2025