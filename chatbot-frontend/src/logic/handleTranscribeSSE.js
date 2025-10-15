export const handleTranscribeSSE = (file, endpoint, onProgress, onChunk, onComplete, onError) => {
  const controller = new AbortController();

  const processStream = async () => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        const events = buffer.split(/\r?\n\r?\n/);
        buffer = events.pop() || '';

        for (const eventText of events) {
          if (!eventText.trim()) continue;

          let eventType = 'message';
          let data = '';

          eventText.split(/\r?\n/).forEach((line) => {
            if (line.startsWith('event:')) {
              eventType = line.substring(6).trim();
            } else if (line.startsWith('data:')) {
              const lineData = line.substring(5);
              // Remove only the first space after 'data:' if present, preserve all other whitespace
              const content = lineData.startsWith(' ') ? lineData.substring(1) : lineData;
              data += (data ? '\n' : '') + content;
            }
          });

          if (data) {
            console.log(`[TRANSCRIBE SSE] ${eventType}:`, data.substring(0, 50));
            
            if (eventType === 'chunk') {
              // Progress messages are short setup messages ending with "..."
              const isProgressMessage = data.length < 50 && data.endsWith('...');
              if (isProgressMessage) {
                onProgress(data);
              } else if (data.startsWith('FINAL:')) {
                // Final complete transcription
                onChunk(data.substring(6), true);
              } else {
                // Partial streaming chunk
                onChunk(data, false);
              }
            } else if (eventType === 'done') {
              onComplete();
            } else if (eventType === 'error') {
              onError(new Error(data));
            }
          }
        }
      }
    } catch (e) {
      console.error('[TRANSCRIBE SSE] Error:', e);
      onError(e);
    }
  };

  processStream();
  return controller;
};
