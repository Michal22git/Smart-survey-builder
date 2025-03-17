import React from 'react';

const ChatInput = ({ inputMessage, setInputMessage, handleSubmit, isGenerating }) => {
  return (
    <form onSubmit={handleSubmit} className="input-form">
      <input
        type="text"
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        placeholder="Describe your survey..."
        className="message-input"
        disabled={isGenerating}
      />
      <button 
        type="submit" 
        className="send-button"
        disabled={isGenerating}
      >
        {isGenerating ? 'Generating...' : 'Send'}
      </button>
    </form>
  );
};

export default ChatInput; 