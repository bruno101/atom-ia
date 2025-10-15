import { useState, useEffect, useCallback } from 'react';
import { saveConversation, getConversation, generateConversationId } from '../utils/conversationStorage';

export const useConversation = () => {
  const [conversationId, setConversationId] = useState(() => generateConversationId());
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content: "Olá! Eu sou **NISA**, uma IA especializada em busca arquivística do S**IA**N.\n\nPosso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nO que você deseja pesquisar hoje?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState("flash");
  const [suggestedLinks, setSuggestedLinks] = useState([]);

  const saveCurrentConversation = useCallback(() => {
    if (messages.length > 1) {
      saveConversation(conversationId, {
        messages,
        input,
        selectedModel,
        suggestedLinks,
        title: messages[1]?.content?.substring(0, 50) || 'Nova conversa'
      });
    }
  }, [conversationId, messages, input, selectedModel, suggestedLinks]);

  useEffect(() => {
    saveCurrentConversation();
  }, [messages, input, selectedModel, suggestedLinks]);

  const loadConversation = useCallback((id) => {
    const conversation = getConversation(id);
    if (conversation) {
      setConversationId(id);
      setMessages(conversation.messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      })));
      setInput(conversation.input || "");
      setSelectedModel(conversation.selectedModel || "flash");
      setSuggestedLinks(conversation.suggestedLinks || []);
    }
  }, []);

  const startNewConversation = useCallback(() => {
    const newId = generateConversationId();
    setConversationId(newId);
    setMessages([
      {
        id: "1",
        role: "assistant",
        content: "Olá! Eu sou **NISA**, uma IA especializada em busca arquivística do S**IA**N.\n\nPosso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nO que você deseja pesquisar hoje?",
        timestamp: new Date(),
      },
    ]);
    setInput("");
    setSelectedModel("flash");
    setSuggestedLinks([]);
  }, []);

  return {
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
  };
};
