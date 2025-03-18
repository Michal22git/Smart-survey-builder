import React from 'react';
import './SurveyCard.css';

const SurveyCard = ({ survey, onDelete, onGenerateReport, onFillSurvey, isGeneratingReport }) => {
  return (
    <div className="survey-card">
      <div className="card-header">
        <h3>{survey.title}</h3>
        <button 
          className="delete-btn"
          onClick={() => onDelete(survey.public_id, survey.title)}
          title="Delete survey"
        >
          &times;
        </button>
      </div>
      <p>Created: {new Date(survey.created_at).toLocaleDateString()}</p>
      {survey.description && <p className="survey-description">{survey.description}</p>}
      <div className="survey-actions">
        <button 
          className="btn primary"
          onClick={() => onFillSurvey(survey.public_id)}
        >
          Fill Survey
        </button>
        <button 
          className="btn secondary"
          onClick={() => onGenerateReport(survey.public_id, survey.title)}
          disabled={isGeneratingReport}
        >
          {isGeneratingReport ? 'Generating...' : 'Generate Report'}
        </button>
      </div>
    </div>
  );
};

export default SurveyCard; 