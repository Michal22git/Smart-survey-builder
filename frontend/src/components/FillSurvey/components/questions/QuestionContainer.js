import React from 'react';
import TextQuestion from './TextQuestion';
import RadioQuestion from './RadioQuestion';
import CheckboxQuestion from './CheckboxQuestion';
import DropdownQuestion from './DropdownQuestion';

const QuestionContainer = ({ question, value, onChange }) => {
  return (
    <div 
      id={`question-${question.id}`}
      className="question-container"
    >
      <div className="question-header">
        <h3 className="question-text">
          {question.text}
          <span className="required-mark">*</span>
        </h3>
      </div>
      
      <div className="answer-container">
        {question.type === 'text' && (
          <TextQuestion 
            value={value || ''} 
            onChange={onChange} 
            required={true}
          />
        )}
        
        {question.type === 'radio' && (
          <RadioQuestion 
            options={question.options}
            questionId={question.id}
            value={value}
            onChange={onChange}
            required={true}
          />
        )}
        
        {question.type === 'checkbox' && (
          <CheckboxQuestion 
            options={question.options}
            questionId={question.id}
            value={Array.isArray(value) ? value : []}
            onChange={onChange}
            required={true}
          />
        )}
        
        {question.type === 'dropdown' && (
          <DropdownQuestion 
            options={question.options}
            value={value || ''}
            onChange={onChange}
            required={true}
          />
        )}
      </div>
    </div>
  );
};

export default QuestionContainer; 