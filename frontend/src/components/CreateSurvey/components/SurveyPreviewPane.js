import React from 'react';
import QuestionRenderer from './QuestionRenderer';

const SurveyPreviewPane = ({ 
  surveyData, 
  isGenerating, 
  isSurveyDone,
  isSaved,
  onSave,
  onRegenerateQuestion 
}) => {
  
  const renderSurveyPreview = () => {
    if (!surveyData) return null;
    
    return (
      <div className="survey-preview-content">
        <h3>{surveyData.title}</h3>
        <p>{surveyData.description}</p>
        
        <div className="survey-questions">
          {surveyData.questions.map((question, index) => (
            <QuestionRenderer 
              key={index}
              question={question}
              index={index}
              onRegenerate={onRegenerateQuestion}
              isGenerating={isGenerating}
            />
          ))}
        </div>
      </div>
    );
  };
  
  return (
    <div className="preview-container">
      <div className="preview-header">
        <h2>Survey Preview</h2>
      </div>
      <div className="preview-content">
        {surveyData ? (
          renderSurveyPreview()
        ) : (
          <div className="preview-placeholder">
            Your survey will appear here while being created through chat.
            Start by describing what kind of survey you want to create!
          </div>
        )}
      </div>
      <div className="preview-actions">
        {isSurveyDone && (
          isSaved ? (
            <button 
              className="saved-survey-btn" 
              disabled={true}
            >
              Survey Saved ✓
            </button>
          ) : (
            <button 
              className="save-survey-btn" 
              onClick={onSave}
              disabled={!surveyData || isGenerating}
            >
              Save Survey
            </button>
          )
        )}
      </div>
    </div>
  );
};

export default SurveyPreviewPane; 