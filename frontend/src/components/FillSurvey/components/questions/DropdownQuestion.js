import React from 'react';

const DropdownQuestion = ({ options, value, onChange, required }) => (
  <select
    value={value}
    onChange={(e) => onChange(e.target.value ? parseInt(e.target.value) : null)}
    className="dropdown-answer"
    required={required}
  >
    <option value="">-- Select an option --</option>
    {options.map((option) => (
      <option key={option.id} value={option.id}>
        {option.text}
      </option>
    ))}
  </select>
);

export default DropdownQuestion; 