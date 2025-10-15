// Componente principal da aplicação SIAN
// Gerencia estado global, layout e orquestração de componentes
import React, { useRef, useEffect, useMemo } from "react";
import "./App.css";
import Header from "./components/Header/Header";
import ChatHeader from "./components/ChatHeader/ChatHeader";
import InputForm from "./components/InputForm/InputForm";
import MessageList from "./components/MessageList/MessageList";
import Sidebar from "./components/Sidebar/Sidebar";
import createHandleSubmit from "./logic/createHandleSubmit";
import Footer from "./components/Footer/Footer";
import { useProgressTimeout } from "./hooks/useProgressTimeout";
import { useConversation } from "./hooks/useConversation";
 
function App() {
  // Hook customizado para gerenciar conversas e persistência
  const {
    conversationId,
    messages,
    setMessages,
    input,
    setInput,
    selectedModel,
    setSelectedModel,
    suggestedLinks,
    setSuggestedLinks,
    loadConversation,
    startNewConversation
  } = useConversation();
  
  // Estados para controle de loading e streaming
  const [isLoading, setIsLoading] = React.useState(false);
  const [currentProgressMessage, setCurrentProgressMessage] = React.useState("");
  const [partialResponse, setPartialResponse] = React.useState("");
  
  // Estados para gerenciamento de arquivos anexados
  const [fileMetadata, setFileMetadata] = React.useState(null);
  const [attachedFile, setAttachedFile] = React.useState(null);

  // Auto-scroll quando novas mensagens são adicionadas
  useEffect(() => {
    scrollToEnd();
  }, [messages]);
 
  // Debug: monitora mudanças de estado para troubleshooting
  useEffect(() => {
    console.log('🔄 APP: isLoading changed to:', isLoading);
  }, [isLoading]);
 
  useEffect(() => {
    console.log('💬 APP: currentProgressMessage changed to:', currentProgressMessage);
  }, [currentProgressMessage]);
 
  useEffect(() => {
    console.log('📝 APP: partialResponse changed, length:', partialResponse?.length || 0);
  }, [partialResponse]);

  // Refs para controle de scroll e cancelamento de requisições
  const scrollAreaRef = useRef(null);
  const abortControllerRef = useRef(null);
  const fileProcessingAbortRef = useRef(null);
  const isIntentionalAbortRef = useRef(false);
 
  // Hook para gerenciar mensagens de progresso automáticas
  const { startProgressTimeout, updateProgressMessage, clearProgressTimeout } = useProgressTimeout(
    isLoading,
    partialResponse,
    setCurrentProgressMessage
  );
 
  // Função para scroll automático até o final da lista de mensagens
  const scrollToEnd = () => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  };
 
  // Memoiza handler de submit para evitar recriações desnecessárias
  const handleSubmit = useMemo(() => createHandleSubmit({
    messages,
    input,
    setMessages,
    setInput,
    setSuggestedLinks,
    isLoading,
    setIsLoading,
    setCurrentProgressMessage: updateProgressMessage,
    setPartialResponse,
    abortControllerRef,
    isIntentionalAbortRef,
    selectedModel,
    scrollToEnd,
    startProgressTimeout,
    clearProgressTimeout,
    fileMetadata,
    setAttachedFile,
    attachedFile
  }), [messages, input, isLoading, selectedModel, attachedFile]);
 
  // Cancela requisições em andamento ao trocar de conversa
  useEffect(() => {
    if (abortControllerRef.current) {
      isIntentionalAbortRef.current = true;
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (fileProcessingAbortRef.current) {
      fileProcessingAbortRef.current.abort();
      fileProcessingAbortRef.current = null;
    }
    clearProgressTimeout();
    setIsLoading(false);
    setCurrentProgressMessage("");
    setPartialResponse("");
    setFileMetadata(null);
    setAttachedFile(null);
  }, [conversationId]);
 
  // Cleanup: limpa timeout quando componente é desmontado
  useEffect(() => {
    return () => {
      clearProgressTimeout();
    };
  }, []);
 
  return (
    <div className="app">
      <Header />
      <div className="main-container">
        <Sidebar
          suggestedLinks={suggestedLinks}
          onNewConversation={startNewConversation}
          onLoadConversation={loadConversation}
          currentConversationId={conversationId}
        />
        <div className="chat-section">
          <div className="chat-container">
            <div className="chat-scrollable" ref={scrollAreaRef}>
              <ChatHeader />
              <MessageList
                messages={messages}
                streamedMessage={currentProgressMessage}
                partialResponse={partialResponse}
                isLoading={isLoading}
              />
            </div>
 
            <div className="input-area">
              <InputForm
                key={conversationId}
                input={input}
                setInput={setInput}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
                setFileMetadata={setFileMetadata}
                attachedFile={attachedFile}
                setAttachedFile={setAttachedFile}
                fileProcessingAbortRef={fileProcessingAbortRef}
              />
              <div className="footer-info">
                <span>Chatbot SIAN • Dataprev © 2025</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
 
export default App;