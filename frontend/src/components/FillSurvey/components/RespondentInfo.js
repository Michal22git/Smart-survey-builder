import React from 'react';

const RespondentInfo = ({ info, onChange }) => (
  <div className="respondent-info">
    <h3>Respondent Information (optional)</h3>
    <div className="form-group">
      <label htmlFor="name">Full Name:</label>
      <input
        type="text"
        id="name"
        name="name"
        value={info.name}
        onChange={onChange}
      />
    </div>
    <div className="form-group">
      <label htmlFor="email">Email:</label>
      <input
        type="email"
        id="email"
        name="email"
        value={info.email}
        onChange={onChange}
      />
    </div>
  </div>
);

export default RespondentInfo; 