const STORAGE_KEY = 'chatbot_conversations';

export const saveConversation = (conversationId, data) => {
  const conversations = getAllConversations();
  conversations[conversationId] = {
    ...data,
    id: conversationId,
    updatedAt: new Date().toISOString()
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
};

export const getConversation = (conversationId) => {
  const conversations = getAllConversations();
  return conversations[conversationId];
};

export const getAllConversations = () => {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : {};
};

export const deleteConversation = (conversationId) => {
  const conversations = getAllConversations();
  delete conversations[conversationId];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
};

export const generateConversationId = () => {
  return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};
