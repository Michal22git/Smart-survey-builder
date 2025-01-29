import React from 'react';
import './SurveyList.css';

const SurveyList = () => {
  const surveys = [
    { id: 1, title: 'Shopping Preferences Survey', date: '2024-01-25' },
    { id: 2, title: 'Customer Satisfaction Survey', date: '2024-01-24' },
  ];

  return (
    <div className="survey-list">
      <h1>Available Surveys</h1>
      <div className="surveys-grid">
        {surveys.map((survey) => (
          <div key={survey.id} className="survey-card">
            <h3>{survey.title}</h3>
            <p>Created: {survey.date}</p>
            <div className="survey-actions">
              <button className="btn primary">Fill Survey</button>
              <button className="btn secondary">Details</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SurveyList; 