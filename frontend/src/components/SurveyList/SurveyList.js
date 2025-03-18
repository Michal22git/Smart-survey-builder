import React, { useState, useEffect } from 'react';
import './SurveyList.css';

const SurveyList = () => {
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSurveys = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/surveys/');
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        setSurveys(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching surveys:', error);
        setError('Nie udało się pobrać ankiet. Spróbuj ponownie później.');
        setLoading(false);
      }
    };

    fetchSurveys();
  }, []);

  if (loading) {
    return (
      <div className="survey-list">
        <h1>Available Surveys</h1>
        <div className="loading">Loading surveys...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="survey-list">
        <h1>Available Surveys</h1>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="survey-list">
      <h1>Available Surveys</h1>
      {surveys.length === 0 ? (
        <div className="no-surveys">No surveys available at the moment.</div>
      ) : (
        <div className="surveys-grid">
          {surveys.map((survey) => (
            <div key={survey.id} className="survey-card">
              <h3>{survey.title}</h3>
              <p>Created: {new Date(survey.created_at).toLocaleDateString()}</p>
              {survey.description && <p className="survey-description">{survey.description}</p>}
              <div className="survey-actions">
                <button className="btn primary">Fill Survey</button>
                <button className="btn secondary">Generate Report</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SurveyList; 