import React from 'react';

const QuestionRenderer = ({ question, index, onRegenerate, isGenerating }) => {
  return (
    <div className="survey-question">
      <div className="question-header">
        <div className="question-number-container">
          <span className="question-number">{index + 1}.</span>
          <button 
            className="regenerate-btn" 
            onClick={() => onRegenerate(index)}
            disabled={isGenerating}
            title="Generate a new version of this question"
          >
            <i className="regenerate-icon">↻</i>
          </button>
        </div>
        <h4>
          {question.text} 
          {question.required && <span className="required">*</span>}
        </h4>
      </div>
      
      <div className="question-content">
        {question.type === 'text' && (
          <input type="text" placeholder="Your answer..." disabled />
        )}
        
        {question.type === 'radio' && question.options && (
          <div className="radio-options">
            {question.options.map((option, optIndex) => (
              <div key={optIndex} className="radio-option">
                <input type="radio" name={`question-${index}`} id={`opt-${index}-${optIndex}`} disabled />
                <label htmlFor={`opt-${index}-${optIndex}`}>{option.text}</label>
              </div>
            ))}
          </div>
        )}
        
        {question.type === 'checkbox' && question.options && (
          <div className="checkbox-options">
            {question.options.map((option, optIndex) => (
              <div key={optIndex} className="checkbox-option">
                <input type="checkbox" id={`opt-${index}-${optIndex}`} disabled />
                <label htmlFor={`opt-${index}-${optIndex}`}>{option.text}</label>
              </div>
            ))}
          </div>
        )}
        
        {question.type === 'dropdown' && question.options && (
          <select disabled>
            <option value="" disabled selected>Select an option</option>
            {question.options.map((option, optIndex) => (
              <option key={optIndex} value={option.text}>{option.text}</option>
            ))}
          </select>
        )}
      </div>
    </div>
  );
};

export default QuestionRenderer; 