import React, { useState, useEffect } from 'react';
import './SurveyList.css';

const SurveyList = () => {
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteMessage, setDeleteMessage] = useState(null);

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

  useEffect(() => {
    fetchSurveys();
  }, []);

  const handleDelete = async (publicId, title) => {
    if (window.confirm(`Czy na pewno chcesz usunąć ankietę "${title}"?`)) {
      try {
        const response = await fetch(`http://localhost:8000/api/surveys/${publicId}/`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        setSurveys(surveys.filter(survey => survey.public_id !== publicId));
        setDeleteMessage(`Ankieta "${title}" została pomyślnie usunięta.`);
        
        setTimeout(() => {
          setDeleteMessage(null);
        }, 3000);
        
      } catch (error) {
        console.error('Error deleting survey:', error);
        setError(`Nie udało się usunąć ankiety: ${error.message}`);
      }
    }
  };

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
      
      {deleteMessage && (
        <div className="success-message">{deleteMessage}</div>
      )}
      
      {surveys.length === 0 ? (
        <div className="no-surveys">No surveys available at the moment.</div>
      ) : (
        <div className="surveys-grid">
          {surveys.map((survey) => (
            <div key={survey.public_id} className="survey-card">
              <div className="card-header">
                <h3>{survey.title}</h3>
                <button 
                  className="delete-btn"
                  onClick={() => handleDelete(survey.public_id, survey.title)}
                  title="Delete survey"
                >
                  &times;
                </button>
              </div>
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