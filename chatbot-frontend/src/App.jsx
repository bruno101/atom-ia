import { useState, useRef, useEffect } from "react";
import "./App.css";
import Header from "./components/Header/Header";
import ChatHeader from "./components/ChatHeader/ChatHeader";
import InputForm from "./components/InputForm/InputForm";
import MessageList from "./components/MessageList/MessageList";
import Sidebar from "./components/Sidebar/Sidebar";
import createHandleSubmit from "./logic/createHandleSubmit";

function App() {

  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content:
        "Olá! Eu sou S**IA**N, uma IA especializada em busca arquivística.\n\nEstou conectada ao banco de dados do AtoM (Access to Memory) e posso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nComo posso auxiliar em sua pesquisa hoje?",
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState("");
  const [suggestedLinks, setSuggestedLinks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentProgressMessage, setCurrentProgressMessage] = useState("");
  const [showSidebar, setShowSidebar] = useState(false);
  const scrollAreaRef = useRef(null);
  const abortControllerRef = useRef(null);

  const handleSubmit = createHandleSubmit({
    messages,
    input,
    setMessages,
    setInput,
    setSuggestedLinks,
    isLoading,
    setIsLoading,
    setCurrentProgressMessage,
    setShowSidebar,
    abortControllerRef,
  });

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages, currentProgressMessage]);

  const toggleSidebar = () => setShowSidebar(!showSidebar);

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
          <ChatHeader />
          <div className="chat-container">
            <MessageList
              messages={messages}
              streamedMessage={currentProgressMessage}
              isLoading={isLoading}
              scrollRef={scrollAreaRef}
            />
            <div className="input-area">
              <InputForm
                input={input}
                setInput={setInput}
                onSubmit={handleSubmit}
                isLoading={isLoading}
              />
              <div className="footer-info">
                <span>Chatbot SIAN • Dataprev © 2025</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
