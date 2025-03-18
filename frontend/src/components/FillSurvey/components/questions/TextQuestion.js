import React from 'react';

const TextQuestion = ({ value, onChange, required }) => (
  <textarea
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder="Type your answer here..."
    className="text-answer"
    required={required}
    rows={4}
  />
);

export default TextQuestion; 