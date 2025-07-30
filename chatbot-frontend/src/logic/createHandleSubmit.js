import buildHistorico from "./buildHistorico";
import fetchSse from "./fetchSse";

export default function createHandleSubmit({
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
}) {
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

  return async function handleSubmit(e) {
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

    const historico = buildHistorico(messages);
    const payload = {
      consulta: input.trim(),
      ...(historico.length > 0 && { historico }),
    };

    const url = process.env.REACT_APP_API_URL;

    abortControllerRef.current = fetchSse(
      url,
      {
        body: payload,
      },
      (event) => {
        //onMessage
        if (event.type === "progress") {
          setCurrentProgressMessage(event.data);
        } else if (event.type === "error") {
          fallbackError(`Erro do servidor: ${event.data}`);
        }
      },
      (error) => {
        //onError
        console.error("HANDLER LOG: 🚫 Erro na conexão SSE (fetch):", error);
        fallbackError(
          "Ocorreu um erro na comunicação com o servidor. Tente novamente."
        );
      },
      (event) => {
        //onDone
        try {
          const data = JSON.parse(event.data);
          const botMessage = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: data.resposta || "Resposta final indisponível.",
            palavras_chave: data.palavras_chave,
            links_analisados: data.links_analisados,
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
        // onOpen
        console.log("HANDLER LOG: 🔌 Conexão SSE estabelecida.");
      },
      () => {
        // onClose
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
}
