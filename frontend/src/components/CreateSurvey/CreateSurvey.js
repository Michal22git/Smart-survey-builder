import React, { useState, useRef, useEffect } from 'react';
import './CreateSurvey.css';

const CreateSurvey = () => {
  const messagesEndRef = useRef(null);
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: 'Hi! I will help you create a survey. Please describe what kind of survey you would like to create.',
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [surveyPreview, setSurveyPreview] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const newMessages = [
      ...messages,
      { type: 'user', content: inputMessage },
    ];
    setMessages(newMessages);
    setInputMessage('');

    setTimeout(() => {
      setMessages([
        ...newMessages,
        {
          type: 'assistant',
          content: 'I understand. Working on it...',
        },
      ]);
    }, 1000);
  };

  const handleSaveSurvey = () => {
    console.log('Saving survey...');
  };

  return (
    <div className="create-survey">
      <div className="survey-layout">
        <div className="chat-container">
          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                <div className="message-content">{message.content}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={handleSubmit} className="input-form">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Describe your survey..."
              className="message-input"
            />
            <button type="submit" className="send-button">
              Send
            </button>
          </form>
        </div>

        <div className="preview-container">
          <div className="preview-header">
            <h2>Survey Preview</h2>
          </div>
          <div className="preview-content">
            {surveyPreview ? (
              surveyPreview
            ) : (
              <div className="preview-placeholder">
                Your survey will appear here as you create it through the chat.
                Start by describing what kind of survey you want to create!
              </div>
            )}
          </div>
          <div className="preview-actions">
            <button 
              className="save-survey-btn" 
              onClick={handleSaveSurvey}
              disabled={!surveyPreview}
            >
              Save Survey
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateSurvey; 