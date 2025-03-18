import React from 'react';

const CheckboxQuestion = ({ options, questionId, value, onChange, required }) => {
  const handleCheckboxChange = (optionId) => {
    if (value.includes(optionId)) {
      onChange(value.filter(id => id !== optionId));
    } else {
      onChange([...value, optionId]);
    }
  };
  
  return (
    <div className="checkbox-options">
      {options.map((option) => (
        <div key={option.id} className="checkbox-option">
          <input
            type="checkbox"
            id={`option-${option.id}`}
            name={`question-${questionId}`}
            value={option.id}
            checked={value.includes(option.id)}
            onChange={() => handleCheckboxChange(option.id)}
          />
          <label htmlFor={`option-${option.id}`}>{option.text}</label>
        </div>
      ))}
      {required && value.length === 0 && (
        <input type="checkbox" required style={{ display: 'none' }} />
      )}
    </div>
  );
};

export default CheckboxQuestion; 