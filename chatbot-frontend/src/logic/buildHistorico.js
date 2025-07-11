const buildHistorico = (messages) => {
  const historico = [];
  for (let i = 1; i < messages.length; i = i + 2) {
    if (messages[i].role === "user" && messages[i + 1]?.role === "assistant") {
      historico.push({
        usuario: messages[i].content,
        bot: messages[i + 1].content,
      });
    }
  }
  return historico;
};

export default buildHistorico;
