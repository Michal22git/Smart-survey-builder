import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SurveyCard from '../SurveyCard/SurveyCard';
import useReportGenerator from '../../hooks/useReportGenerator';
import './SurveyList.css';

const SurveyList = () => {
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteMessage, setDeleteMessage] = useState(null);
  const navigate = useNavigate();
  
  const { 
    isGeneratingReport, 
    reportError, 
    generateReport, 
    clearReportError 
  } = useReportGenerator();

  // Fetch surveys
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
        setError('Failed to load surveys. Please try again later.');
        setLoading(false);
      }
    };

    fetchSurveys();
  }, []);

  // Delete survey
  const handleDelete = async (publicId, title) => {
    if (window.confirm(`Are you sure you want to delete the survey "${title}"?`)) {
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
        setDeleteMessage(`Survey "${title}" has been successfully deleted.`);
        
        setTimeout(() => {
          setDeleteMessage(null);
        }, 3000);
        
      } catch (error) {
        console.error('Error deleting survey:', error);
        setError(`Failed to delete survey: ${error.message}`);
      }
    }
  };

  // Generate report
  const handleGenerateReport = (publicId, title) => {
    generateReport(publicId, title);
  };
  
  // Fill survey - navigate to the survey form
  const handleFillSurvey = (publicId) => {
    console.log('Navigating to fill survey:', publicId);
    navigate(`/surveys/${publicId}/fill`);
  };

  // Loading view
  if (loading) {
    return (
      <div className="survey-list">
        <h1>Available Surveys</h1>
        <div className="loading">Loading surveys...</div>
      </div>
    );
  }

  // Error view
  if (error) {
    return (
      <div className="survey-list">
        <h1>Available Surveys</h1>
        <div className="error">{error}</div>
      </div>
    );
  }

  // Main survey list view
  return (
    <div className="survey-list">
      <h1>Available Surveys</h1>
      
      {deleteMessage && (
        <div className="success-message">{deleteMessage}</div>
      )}
      
      {reportError && (
        <div className="error">{reportError}</div>
      )}
      
      {surveys.length === 0 ? (
        <div className="no-surveys">No surveys available.</div>
      ) : (
        <div className="surveys-grid">
          {surveys.map((survey) => (
            <SurveyCard
              key={survey.public_id}
              survey={survey}
              onDelete={handleDelete}
              onGenerateReport={handleGenerateReport}
              onFillSurvey={handleFillSurvey}
              isGeneratingReport={isGeneratingReport}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default SurveyList; 