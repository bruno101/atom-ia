import ArchiveIcon from "./icons/ArchiveIcon";
import UserIcon from "./icons/UserIcon";
import formatTime from "../utils/formatTime";

const ChatMessage = ({ message }) => {
  const isUser = message.role === "user";
  return (
    <div className={`message ${isUser ? "message-user" : "message-assistant"}`}>
      {!isUser && <div className="message-avatar message-avatar-bot"><ArchiveIcon /></div>}
      <div className={`message-bubble ${isUser ? "bubble-user" : "bubble-assistant"}`}>
        <div className="message-content">{message.content}</div>
        <div className="message-time">
          <div className="time-dot"></div>
          {formatTime(message.timestamp)}
        </div>
      </div>
      {isUser && <div className="message-avatar message-avatar-user"><UserIcon /></div>}
    </div>
  );
};

export default ChatMessage;
