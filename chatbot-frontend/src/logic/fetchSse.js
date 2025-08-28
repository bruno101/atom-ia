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
      console.log(url)
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
      if (onError) onError(e);
    }
  };

  processStream();
  return controller;
};

export default fetchSse;
