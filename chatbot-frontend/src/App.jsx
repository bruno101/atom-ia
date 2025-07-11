import { useState, useRef, useEffect } from "react";
import "./App.css";
import ChatHeader from "./components/ChatHeader/ChatHeader";
import InputForm from "./components/InputForm/InputForm";
import MessageList from "./components/MessageList/MessageList";
import Sidebar from "./components/Sidebar/Sidebar";

const fetchSse = (
  url,
  options,
  onMessage,
  onError,
  onDone,
  onOpen,
  onClose
) => {
  const controller = new AbortController();

  const processStream = async () => {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          ...options.headers,
        },
        body: JSON.stringify(options.body),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `HTTP error! status: ${response.status}, message: ${errorText}`
        );
      }

      if (onOpen) onOpen();

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          if (buffer.trim()) {
            processEventsFromBuffer(true);
          }
          if (onClose) onClose();
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;


        processEventsFromBuffer(false);
      }

      function processEventsFromBuffer(isEndOfStream) {

        const events = buffer.split(/\r?\n\r?\n/);

        if (!isEndOfStream) {
          buffer = events.pop() || "";
        }


        for (const eventText of events) {
          if (!eventText.trim()) {
            continue;
          }


          let eventType = "message";
          let data = "";
          let id = null;

          eventText.split(/\r?\n/).forEach((line) => {
            if (line.startsWith("event:")) {
              eventType = line.substring(6).trim();
            } else if (line.startsWith("data:")) {
              data += (data ? "\n" : "") + line.substring(5).trim();
            } else if (line.startsWith("id:")) {
              id = line.substring(4).trim();
            }
          });

          if (data) {
            const eventPayload = { data, type: eventType, id };
            if (eventType === "done" && onDone) {
              onDone(eventPayload);
            } else if (onMessage) {
              onMessage(eventPayload);
            }
          } 
        }
      }
    } catch (e) {
      if (e.name === "AbortError") {
        console.log("[SSE DEBUG] 🛑 Fetch stream aborted by user.");
      } else {
        console.error("❌ [SSE DEBUG] Fetch SSE error:", e);
        if (onError) onError(e);
      }
    }
  };

  processStream();
  return controller;
};

function App() {
  

  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content:
        "Olá! Eu sou ModestIA, uma IA especializada em busca arquivística.\n\nEstou conectada ao banco de dados do AtoM (Access to Memory) e posso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nComo posso auxiliar em sua pesquisa hoje?",
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



  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages, currentProgressMessage]);


  const buildHistorico = () => {
    const historico = [];
    for (let i = 1; i < messages.length; i=i+2) {
      if (
        messages[i].role === "user" &&
        messages[i + 1]?.role === "assistant"
      ) {
        historico.push({
          usuario: messages[i].content,
          bot: messages[i + 1].content,
        });
      }
    }
    return historico;
  };

  const fallbackError = (content) => {
    setIsLoading(false);
    setMessages((prev) => [
      ...prev,
      {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content,
        timestamp: new Date(),
      },
    ]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setCurrentProgressMessage("");
    setIsLoading(true);
    setSuggestedLinks([]);

    const historico = buildHistorico();
    const payload = {
      consulta: input.trim(),
      ...(historico.length > 0 && { historico }),
    };

    const url = "http://localhost:7860/ask-stream";

    abortControllerRef.current = fetchSse(
      url,
      {
        body: payload,
      },
      (event) => {
        if (event.type === "progress") {
          setCurrentProgressMessage(event.data); // Replace instead of append
        } else if (event.type === "error") {
          fallbackError(`Erro do servidor: ${event.data}`);
        }
      },
      (error) => {
        console.error("HANDLER LOG: 🚫 Erro na conexão SSE (fetch):", error);
        fallbackError(
          "Ocorreu um erro na comunicação com o servidor. Tente novamente."
        );
      },
      (event) => {
        try {
          const data = JSON.parse(event.data);
          const botMessage = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: data.resposta || "Resposta final indisponível.",
            timestamp: new Date(),
          };

          setMessages((prev) => {
            const newMessages = [...prev, botMessage];
            return newMessages;
          });
          setCurrentProgressMessage("");
          setIsLoading(false);

          if (Array.isArray(data.links)) {
            setSuggestedLinks(data.links);
            if (window.innerWidth <= 768) setShowSidebar(true);
          }
        } catch (err) {
          console.error(
            "HANDLER LOG: ❌ Erro ao parsear resposta do evento 'done':",
            err
          );
          fallbackError("Erro ao processar a resposta final.");
        } finally {
          abortControllerRef.current = null;
        }
      },
      () => {
        // onOpen handler
        console.log("HANDLER LOG: 🔌 Conexão SSE estabelecida.");
      },
      () => {
        // onClose handler
        console.log("HANDLER LOG: Stream da API concluído.");
        if (isLoading) {
          fallbackError(
            "A conexão com o servidor foi encerrada inesperadamente."
          );
        }
        abortControllerRef.current = null;
      }
    );
  };

  const toggleSidebar = () => setShowSidebar(!showSidebar);

  return (
    <div className="app">
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
