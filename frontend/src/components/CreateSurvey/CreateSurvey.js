import React, { useState, useRef, useEffect } from 'react';
import './CreateSurvey.css';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import SurveyPreviewPane from './components/SurveyPreviewPane';
import FeedbackDialog from './components/FeedbackDialog';

const CreateSurvey = () => {
  const messagesEndRef = useRef(null);
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: 'Hello! I will help you create a survey. Describe what kind of survey you want to create.',
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [surveyPreview, setSurveyPreview] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [webSocket, setWebSocket] = useState(null);
  const [surveyPrompt, setSurveyPrompt] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');
  const [feedbackInput, setFeedbackInput] = useState('');
  const [questionToRegenerate, setQuestionToRegenerate] = useState(null);
  const [isSurveyDone, setIsSurveyDone] = useState(false);
  const [isSurveyDataSaved, setIsSurveyDataSaved] = useState(false);
  const [savedSurveyId, setSavedSurveyId] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/survey/generate/');
    
    ws.onopen = () => {
      console.log('WebSocket connection established');
    };
    
    ws.onmessage = (event) => {
      handleWebSocketMessage(event);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      addBotMessage('There was a connection problem. Try refreshing the page.');
    };
    
    ws.onclose = () => {
      console.log('WebSocket connection closed');
      addBotMessage('The connection was interrupted. Try refreshing the page.');
    };
    
    setWebSocket(ws);
    
    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'connection_established':
          console.log('Connection established:', data.message);
          break;
          
        case 'generation_started':
          setIsGenerating(true);
          setIsSurveyDataSaved(false);
          setSavedSurveyId(null);
          addBotMessage('Starting to generate the survey...');
          break;
          
        case 'generation_chunk':
          setGeneratedContent(prev => prev + data.content);
          break;
          
        case 'generation_complete':
          setIsGenerating(false);
          setIsSurveyDone(true);
          addBotMessage('The survey has been generated!');
          setSurveyPreview(data.survey);
          break;
          
        case 'regeneration_started':
          setIsGenerating(true);
          addBotMessage(`Regenerating question ${data.question_index + 1}...`);
          break;
          
        case 'regeneration_complete':
          setIsGenerating(false);
          setIsSurveyDataSaved(false);
          setSurveyPreview(data.survey);
          setGeneratedContent(JSON.stringify(data.survey));
          addBotMessage(`Question ${data.regenerated_index + 1} has been updated!`);
          break;
          
        case 'survey_saved':
          setIsSurveyDataSaved(true);
          setSavedSurveyId(data.survey_data.id);
          addBotMessage(`Survey "${data.survey_data.title}" has been saved successfully!`);
          break;
          
        case 'error':
          setIsGenerating(false);
          addBotMessage(`An error occurred: ${data.message}`);
          break;
          
        default:
          console.log('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('Error processing WebSocket message:', error);
    }
  };

  const addBotMessage = (content) => {
    setMessages(prevMessages => [
      ...prevMessages,
      { type: 'assistant', content }
    ]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !webSocket) return;

    setSurveyPrompt(inputMessage);
    
    const newMessages = [
      ...messages,
      { type: 'user', content: inputMessage },
    ];
    setMessages(newMessages);
    setInputMessage('');
    setGeneratedContent('');

    if (webSocket.readyState === WebSocket.OPEN) {
      webSocket.send(JSON.stringify({
        type: 'generate_survey',
        prompt: inputMessage,
        num_questions: 5,
        template: 'general',
        stream: true
      }));
      
      setIsGenerating(true);
    } else {
      addBotMessage('No connection to server. Try refreshing the page.');
    }
  };

  const handleSaveSurvey = () => {
    if (!webSocket || !surveyPreview) return;
    
    if (webSocket.readyState === WebSocket.OPEN) {
      webSocket.send(JSON.stringify({
        type: 'save_survey',
        survey: JSON.parse(generatedContent),
        prompt: surveyPrompt
      }));
      
      addBotMessage('Saving the survey...');
    } else {
      addBotMessage('No connection to server. Try refreshing the page.');
    }
  };

  const handleRegenerateQuestion = (questionIndex) => {
    setQuestionToRegenerate(questionIndex);
    setFeedbackInput('');
  };

  const submitFeedback = () => {
    if (questionToRegenerate === null) return;
    
    if (!webSocket || webSocket.readyState !== WebSocket.OPEN) {
      addBotMessage('No connection to server. Try refreshing the page.');
      setQuestionToRegenerate(null);
      return;
    }
    
    let surveyData;
    try {
      surveyData = JSON.parse(generatedContent);
    } catch (e) {
      console.error('JSON parsing error:', e);
      addBotMessage('There was a problem with the survey data. Try generating a new survey.');
      setQuestionToRegenerate(null);
      return;
    }
    
    const feedback = feedbackInput.trim() || 'Please provide a better question';
    webSocket.send(JSON.stringify({
      type: 'regenerate_question',
      survey: surveyData,
      question_index: questionToRegenerate,
      feedback: feedback
    }));
    
    setIsGenerating(true);
    addBotMessage(`Regenerating question ${questionToRegenerate + 1} with your suggestion...`);
    setQuestionToRegenerate(null); 
  };

  return (
    <div className="create-survey">
      {questionToRegenerate !== null && (
        <FeedbackDialog 
          questionIndex={questionToRegenerate}
          feedbackInput={feedbackInput}
          setFeedbackInput={setFeedbackInput}
          onCancel={() => setQuestionToRegenerate(null)}
          onSubmit={submitFeedback}
        />
      )}
      <div className="survey-layout">
        <div className="chat-container">
          <ChatMessages 
            messages={messages} 
          />
          
          <ChatInput 
            inputMessage={inputMessage}
            setInputMessage={setInputMessage}
            handleSubmit={handleSubmit}
            isGenerating={isGenerating}
          />
        </div>

        <SurveyPreviewPane
          surveyData={surveyPreview}
          isGenerating={isGenerating}
          isSurveyDone={isSurveyDone}
          isSaved={isSurveyDataSaved}
          savedId={savedSurveyId}
          onSave={handleSaveSurvey}
          onRegenerateQuestion={handleRegenerateQuestion}
        />
      </div>
    </div>
  );
};

export default CreateSurvey; 