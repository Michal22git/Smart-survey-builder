import React from 'react';

const RadioQuestion = ({ options, questionId, value, onChange, required }) => (
  <div className="radio-options">
    {options.map((option) => (
      <div key={option.id} className="radio-option">
        <input
          type="radio"
          id={`option-${option.id}`}
          name={`question-${questionId}`}
          value={option.id}
          checked={value === option.id}
          onChange={() => onChange(option.id)}
          required={required && !value}
        />
        <label htmlFor={`option-${option.id}`}>{option.text}</label>
      </div>
    ))}
  </div>
);

export default RadioQuestion; 