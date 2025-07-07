"use client"

import { useState, useRef, useEffect } from "react"
import "./App.css"

// Simple icon components
const ArchiveIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="2" y="3" width="20" height="5" rx="1" />
    <path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8" />
    <path d="M10 12h4" />
  </svg>
)

const UserIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
)

const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M22 2L11 13" />
    <path d="M22 2L15 22L11 13L2 9L22 2Z" />
  </svg>
)

const LoaderIcon = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    className="animate-spin"
  >
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
)

const SearchIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8" />
    <path d="M21 21L16.65 16.65" />
  </svg>
)

const FileTextIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14,2 14,8 20,8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <polyline points="10,9 9,9 8,9" />
  </svg>
)

const DatabaseIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
  </svg>
)

function App() {
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content:
        "Olá! Eu sou o ModestIA, seu assistente especializado em busca arquivística.\n\nEstou conectado ao banco de dados do AtoM (Access to Memory) e posso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nComo posso auxiliar em sua pesquisa hoje?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef(null)

  // Scroll to last message
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  // Convert messages to history format
  const buildHistorico = () => {
    const historico = []

    for (let i = 1; i < messages.length; i += 2) {
      if (messages[i] && messages[i + 1]) {
        historico.push({
          usuario: messages[i].content,
          bot: messages[i + 1].content,
        })
      }
    }

    return historico
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      // Prepare payload based on history
      const historico = buildHistorico()
      const payload =
        historico.length > 0
          ? {
              consulta: input.trim(),
              historico: historico,
            }
          : {
              consulta: input.trim(),
            }

      // Modesto IA specific endpoint
      const response = await fetch("http://localhost:7860/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error("Erro na comunicação com o servidor AtoM")
      }

      const data = await response.json()

      const botMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.resposta || "Desculpe, não consegui processar sua consulta arquivística.",
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, botMessage])
    } catch (error) {
      console.error("Erro:", error)
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "Desculpe, ocorreu um erro ao consultar o banco de dados do AtoM. Verifique se o serviço está disponível e tente novamente.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const formatTime = (date) => {
    return date.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div className="header-main">
            <div className="logo">
              <ArchiveIcon />
            </div>
            <div className="header-text">
              <h1>ModestIA</h1>
              <p>Assistente Especializado em Busca Arquivística</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        <div className="chat-card">
          <div className="chat-header">
            <div className="chat-header-icon">
              <ArchiveIcon />
            </div>
            <div className="chat-header-text">
              <div className="chat-title">Consulta Arquivística</div>
              <div className="chat-subtitle">Powered by AtoM • Dataprev</div>
            </div>
          </div>

          <div className="chat-content">
            {/* Messages Area */}
            <div className="messages-area" ref={scrollAreaRef}>
              <div className="messages-container">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`message ${message.role === "user" ? "message-user" : "message-assistant"}`}
                  >
                    {message.role === "assistant" && (
                      <div className="message-avatar message-avatar-bot">
                        <ArchiveIcon />
                      </div>
                    )}

                    <div className={`message-bubble ${message.role === "user" ? "bubble-user" : "bubble-assistant"}`}>
                      <div className="message-content">{message.content}</div>
                      <div className="message-time">
                        <div className="time-dot"></div>
                        {formatTime(message.timestamp)}
                      </div>
                    </div>

                    {message.role === "user" && (
                      <div className="message-avatar message-avatar-user">
                        <UserIcon />
                      </div>
                    )}
                  </div>
                ))}

                {isLoading && (
                  <div className="message message-assistant">
                    <div className="message-avatar message-avatar-bot">
                      <ArchiveIcon />
                    </div>
                    <div className="message-bubble bubble-assistant">
                      <div className="loading-content">
                        <LoaderIcon />
                        <span>Consultando banco de dados AtoM...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Input Area */}
            <div className="input-area">
              <form onSubmit={handleSubmit} className="input-form">
                <div className="input-container">
                  <div className="input-icon">
                    <SearchIcon />
                  </div>
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Digite sua consulta arquivística (ex: documentos sobre ciclo da borracha, fundos do século XIX...)"
                    className="input-field"
                    disabled={isLoading}
                  />
                </div>
                <button type="submit" disabled={!input.trim() || isLoading} className="submit-button">
                  {isLoading ? (
                    <LoaderIcon />
                  ) : (
                    <>
                      <SendIcon />
                      <span>Consultar</span>
                    </>
                  )}
                </button>
              </form>

              <div className="footer-info">
                <div className="status-indicator">
                  <div className="status-dot"></div>
                  <span>AtoM Online</span>
                </div>
                <div className="footer-separator"></div>
                <span>ModestIA v1.0</span>
                <div className="footer-separator"></div>
                <span>Dataprev © 2025</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
