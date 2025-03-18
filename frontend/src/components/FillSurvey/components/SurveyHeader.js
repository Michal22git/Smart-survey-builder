import React from 'react';

const SurveyHeader = ({ title, description }) => (
  <div className="survey-header">
    <h1>{title}</h1>
    {description && <p className="survey-description">{description}</p>}
    <p className="all-required-notice">All questions require an answer</p>
  </div>
);

export default SurveyHeader; 