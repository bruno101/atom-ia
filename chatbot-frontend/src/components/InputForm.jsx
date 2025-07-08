import { useState } from "react";
import SearchIcon from "./icons/SearchIcon";
import SendIcon from "./icons/SendIcon";
import LoaderIcon from "./icons/LoaderIcon";

const InputForm = ({ input, setInput, onSubmit, isLoading }) => (
  <form onSubmit={onSubmit} className="input-form">
    <div className="input-container">
      <div className="input-icon"><SearchIcon /></div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Digite sua consulta..."
        className="input-field"
        disabled={isLoading}
      />
    </div>
    <button type="submit" disabled={!input.trim() || isLoading} className="submit-button">
      {isLoading ? <LoaderIcon /> : <><SendIcon /><span className="submit-text">Consultar</span></>}
    </button>
  </form>
);

export default InputForm;
