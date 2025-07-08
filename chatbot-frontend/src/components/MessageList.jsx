import ChatMessage from "./ChatMessage";
import LoaderIcon from "./icons/LoaderIcon";
import ArchiveIcon from "./icons/ArchiveIcon";

const MessageList = ({ messages, isLoading, scrollRef }) => (
  <div className="messages-area" ref={scrollRef}>
    <div className="messages-container">
      {messages.map((m) => <ChatMessage key={m.id} message={m} />)}
      {isLoading && (
        <div className="message message-assistant">
          <div className="message-avatar message-avatar-bot"><ArchiveIcon /></div>
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
);

export default MessageList;
