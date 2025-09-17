import { useState, useRef, useEffect, useMemo } from "react";
import "./App.css";
import Header from "./components/Header/Header";
import ChatHeader from "./components/ChatHeader/ChatHeader";
import InputForm from "./components/InputForm/InputForm";
import MessageList from "./components/MessageList/MessageList";
import Sidebar from "./components/Sidebar/Sidebar";
import createHandleSubmit from "./logic/createHandleSubmit";
import Footer from "./components/Footer/Footer";
import { useProgressTimeout } from "./hooks/useProgressTimeout";
 
function App() {
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content:
        "Olá! Eu sou **NISA**, uma IA especializada em busca arquivística.\n\nPosso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nO que você deseja pesquisar hoje?",
      timestamp: new Date(),
    },
  ]);
 
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState("flash");
  const [suggestedLinks, setSuggestedLinks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentProgressMessage, setCurrentProgressMessage] = useState("");
  const [partialResponse, setPartialResponse] = useState("");
 
  // Debug logging para mudanças de estado
  useEffect(() => {
    console.log('🔄 APP: isLoading changed to:', isLoading);
  }, [isLoading]);
 
  useEffect(() => {
    console.log('💬 APP: currentProgressMessage changed to:', currentProgressMessage);
  }, [currentProgressMessage]);
 
  useEffect(() => {
    console.log('📝 APP: partialResponse changed, length:', partialResponse?.length || 0);
  }, [partialResponse]);
  const [showSidebar, setShowSidebar] = useState(false);
  const scrollAreaRef = useRef(null);
  const abortControllerRef = useRef(null);
 
 
 
  const { startProgressTimeout, updateProgressMessage, clearProgressTimeout } = useProgressTimeout(
    isLoading,
    partialResponse,
    setCurrentProgressMessage
  );
 
  const scrollToEnd = () => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  };
 
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
    setShowSidebar,
    abortControllerRef,
    selectedModel,
    scrollToEnd,
    startProgressTimeout,
    clearProgressTimeout,
  }), [messages, input, isLoading, selectedModel]);
 
 
 
  const toggleSidebar = () => setShowSidebar(!showSidebar);
 
  // Cleanup do timeout quando o componente for desmontado
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
          showSidebar={showSidebar}
          toggleSidebar={toggleSidebar}
          suggestedLinks={suggestedLinks}
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
      <Footer />
    </div>
  );
}
 
export default App;