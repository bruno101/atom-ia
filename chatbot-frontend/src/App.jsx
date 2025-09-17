import { useState, useRef, useEffect, useMemo } from "react";
import "./App.css";
import Header from "./components/Header/Header";
import ChatHeader from "./components/ChatHeader/ChatHeader";
import InputForm from "./components/InputForm/InputForm";
import MessageList from "./components/MessageList/MessageList";
import Sidebar from "./components/Sidebar/Sidebar";
import createHandleSubmit from "./logic/createHandleSubmit";
import Footer from "./components/Footer/Footer";

/**
 * Componente principal da aplicação SIAN
 * Gerencia o estado global e orquestra a comunicação entre componentes
 */
function App() {
  // Estado das mensagens do chat com mensagem inicial de boas-vindas
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content:
        "Olá! Eu sou S**IA**N, uma IA especializada em busca arquivística.\n\nPosso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nO que você deseja pesquisar hoje?",
      timestamp: new Date(),
    },
  ]);

  // Estados do formulário de entrada
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState("flash");
  
  // Estados da sidebar e links sugeridos
  const [suggestedLinks, setSuggestedLinks] = useState([]);
  const [showSidebar, setShowSidebar] = useState(false);
  
  // Estados de carregamento e streaming
  const [isLoading, setIsLoading] = useState(false);
  const [currentProgressMessage, setCurrentProgressMessage] = useState("");
  const [partialResponse, setPartialResponse] = useState("");
  
  // Referências para controle de scroll e cancelamento de requisições
  const scrollAreaRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Função para rolar automaticamente para o final do chat
  const scrollToEnd = () => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  };

  // Memoiza a função de envio para evitar recriações desnecessárias
  const handleSubmit = useMemo(() => createHandleSubmit({
    messages,
    input,
    setMessages,
    setInput,
    setSuggestedLinks,
    isLoading,
    setIsLoading,
    setCurrentProgressMessage,
    setPartialResponse,
    setShowSidebar,
    abortControllerRef,
    selectedModel,
    scrollToEnd,
  }), [messages, input, isLoading, selectedModel]);

  // Alterna a visibilidade da sidebar
  const toggleSidebar = () => setShowSidebar(!showSidebar);

  return (
    <div className="app">
      {/* Cabeçalho institucional */}
      <Header />
      
      <div className="main-container">
        {/* Sidebar com links sugeridos */}
        <Sidebar
          showSidebar={showSidebar}
          toggleSidebar={toggleSidebar}
          suggestedLinks={suggestedLinks}
        />
        
        {/* Área principal do chat */}
        <div className="chat-section">
          <div className="chat-container">
            {/* Área rolável do chat */}
            <div className="chat-scrollable" ref={scrollAreaRef}>
              <ChatHeader />
              <MessageList
                messages={messages}
                streamedMessage={currentProgressMessage}
                partialResponse={partialResponse}
                isLoading={isLoading}
              />
            </div>

            {/* Área de entrada fixa na parte inferior */}
            <div className="input-area">
              <InputForm
                input={input}
                setInput={setInput}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
              />
              <div className="footer-info">
                <span>Chatbot SIAN • Dataprev © 2025</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Rodapé institucional */}
      <Footer />
    </div>
  );
}

export default App;
