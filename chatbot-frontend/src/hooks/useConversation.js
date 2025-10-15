// Hook customizado para gerenciamento de conversas
// Gerencia estado, persistência e navegação entre conversas
import { useState, useEffect, useCallback } from 'react';
import { saveConversation, getConversation, generateConversationId } from '../utils/conversationStorage';

export const useConversation = () => {
  // Estado da conversa atual
  const [conversationId, setConversationId] = useState(() => generateConversationId());
  
  // Mensagens da conversa (inicializa com mensagem de boas-vindas)
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content: "Olá! Eu sou **NISA**, uma IA especializada em busca arquivística do S**IA**N.\n\nPosso ajudá-lo a encontrar documentos, fundos arquivísticos, séries documentais e informações históricas.\n\nO que você deseja pesquisar hoje?",
      timestamp: new Date(),
    },
  ]);
  
  // Estado do input e configurações
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState("flash");
  const [suggestedLinks, setSuggestedLinks] = useState([]);

  // Salva conversa atual no localStorage
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

  // Auto-save: salva conversa sempre que houver mudanças
  useEffect(() => {
    saveCurrentConversation();
  }, [messages, input, selectedModel, suggestedLinks]);

  // Carrega conversa existente do localStorage
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

  // Inicia nova conversa com estado limpo
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
