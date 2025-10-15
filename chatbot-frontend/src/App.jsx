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
  const [isLoading, setIsLoading] = React.useState(false);
  const [currentProgressMessage, setCurrentProgressMessage] = React.useState("");
  const [partialResponse, setPartialResponse] = React.useState("");
  const [fileMetadata, setFileMetadata] = React.useState(null);
  const [attachedFile, setAttachedFile] = React.useState(null);

  useEffect(() => {
    scrollToEnd();
  }, [messages]);
 
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

    abortControllerRef,
    selectedModel,
    scrollToEnd,
    startProgressTimeout,
    clearProgressTimeout,
    fileMetadata,
    setAttachedFile,
    attachedFile
  }), [messages, input, isLoading, selectedModel, attachedFile]);
 
 
 

 
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
                input={input}
                setInput={setInput}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
                setFileMetadata={setFileMetadata}
                attachedFile={attachedFile}
                setAttachedFile={setAttachedFile}
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