import { useState, useRef, useEffect } from "react";
import "./App.css";
import ChatHeader from "./components/ChatHeader/ChatHeader";
import InputForm from "./components/InputForm/InputForm";
import MessageList from "./components/MessageList/MessageList";
import Sidebar from "./components/Sidebar/Sidebar";

function App() {
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content:
        "Olá! Eu sou o ModestIA, seu assistente especializado em busca arquivística.\n\nEstou conectado ao banco de dados do AtoM (Access to Memory) e posso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nComo posso auxiliar em sua pesquisa hoje?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedLinks, setSuggestedLinks] = useState([]);
  const scrollAreaRef = useRef(null);
  const [showSidebar, setShowSidebar] = useState(false);

  // Deslizar para a última mensagem quando novas mensagens são adicionadas
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Converter mensagens para formato de histórico
  const buildHistorico = () => {
    const historico = [];

    for (let i = 1; i < messages.length; i += 2) {
      if (messages[i] && messages[i + 1]) {
        historico.push({
          usuario: messages[i].content,
          bot: messages[i + 1].content,
        });
      }
    }

    return historico;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Preparando payload
      const historico = buildHistorico();
      const payload =
        historico.length > 0
          ? {
              consulta: input.trim(),
              historico: historico,
            }
          : {
              consulta: input.trim(),
            };

      // Acessando endpoint do ModestIA
      const response = await fetch("http://localhost:7860/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Erro na comunicação com o servidor AtoM");
      }

      const data = await response.json();

      const botMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          data.resposta ||
          "Desculpe, não consegui processar sua consulta arquivística.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);

      // Atualizar links sugeridos
      if (data.links && Array.isArray(data.links)) {
        setSuggestedLinks(data.links);
        // No celular, mostrar sidebar se links estão disponíveis
        if (window.innerWidth <= 768) {
          setShowSidebar(true);
        }
      }
    } catch (error) {
      console.error("Erro:", error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "Desculpe, ocorreu um erro ao consultar o banco de dados do AtoM. Verifique se o serviço está disponível e tente novamente.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };


  const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
  };

  return (
    <div className="app">
      <div className="main-container">

        <Sidebar showSidebar={showSidebar} toggleSidebar={toggleSidebar} suggestedLinks={suggestedLinks}/>

        <div className="chat-section">

          <ChatHeader/>

          <div className="chat-container">

            <MessageList messages={messages} isLoading={isLoading} scrollRef={scrollAreaRef}/>

            <div className="input-area">
              
              <InputForm input={input} setInput={setInput} onSubmit={handleSubmit} isLoading={isLoading}/>

              <div className="footer-info">
                <span>ModestIA • Powered by AtoM • Dataprev © 2025</span>
              </div>

            </div>

          </div>

        </div>

      </div>
    </div>
  );
}

export default App;
