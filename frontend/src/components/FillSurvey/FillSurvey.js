import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './FillSurvey.css';

import SurveyHeader from './components/SurveyHeader';
import LoadingState from './components/LoadingState';
import ErrorState from './components/ErrorState';
import SuccessState from './components/SuccessState';
import QuestionContainer from './components/questions/QuestionContainer';
import RespondentInfo from './components/RespondentInfo';
import FormActions from './components/FormActions';

import { formatAnswersForSubmission } from './utils/answerFormatters';

const FillSurvey = () => {
  const { publicId } = useParams();
  const navigate = useNavigate();
  
  const [survey, setSurvey] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [respondentInfo, setRespondentInfo] = useState({
    name: '',
    email: ''
  });

  useEffect(() => {
    const fetchSurveyDetails = async () => {
      try {
        setLoading(true);
        console.log('Fetching survey details for ID:', publicId);
        const response = await fetch(`http://localhost:8000/api/surveys/${publicId}/details/`);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Server error:', errorText);
          throw new Error(`HTTP Error! Status: ${response.status}, Details: ${errorText}`);
        }
        
        const data = await response.json();
        setSurvey(data);
        
        if (data.schema && data.schema.questions) {
          const initialAnswers = {};
          data.schema.questions.forEach(question => {
            if (question.type === 'text') {
              initialAnswers[question.id] = '';
            } else if (question.type === 'checkbox') {
              initialAnswers[question.id] = [];
            } else {
              initialAnswers[question.id] = null;
            }
          });
          setAnswers(initialAnswers);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching survey:', error);
        setError('Failed to load survey. Please check if the URL is correct.');
        setLoading(false);
      }
    };
    
    fetchSurveyDetails();
  }, [publicId]);

  useEffect(() => {
    if (submitSuccess) {
      const redirectTimer = setTimeout(() => {
        navigate('/');
      }, 3000);
      
      return () => clearTimeout(redirectTimer);
    }
  }, [submitSuccess, navigate]);

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleRespondentInfoChange = (e) => {
    const { name, value } = e.target;
    setRespondentInfo(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const requiredQuestions = survey.schema.questions;
    const unansweredQuestions = requiredQuestions.filter(q => {
      const answer = answers[q.id];
      if (answer === null || answer === undefined) return true;
      if (Array.isArray(answer) && answer.length === 0) return true;
      if (answer === '') return true;
      return false;
    });
    
    if (unansweredQuestions.length > 0) {
      alert(`Please answer all questions (${unansweredQuestions.length} remaining)`);
      return;
    }
    
    try {
      setSubmitting(true);
      
      const answersToSubmit = formatAnswersForSubmission(answers, survey.schema.questions);
      
      const responseData = {
        respondent_name: respondentInfo.name,
        respondent_email: respondentInfo.email,
        answers: answersToSubmit
      };
      
      const response = await fetch(`http://localhost:8000/api/surveys/${publicId}/respond/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(responseData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Response error:', errorData);
        throw new Error(`${response.status}, ${JSON.stringify(errorData)}`);
      }
      
      setSubmitSuccess(true);
      setSubmitting(false);
    } catch (error) {
      console.error('Error submitting response:', error);
      setError(`Failed to submit response: ${error.message}`);
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (submitSuccess) return <SuccessState />;
  if (!survey) return <ErrorState message="Survey not found with the given identifier." />;

  return (
    <div className="fill-survey">
      <SurveyHeader title={survey.title} description={survey.description} />
      
      <form onSubmit={handleSubmit}>
        {survey.schema.questions.map((question) => (
          <QuestionContainer 
            key={question.id}
            question={question}
            value={answers[question.id]}
            onChange={(value) => handleAnswerChange(question.id, value)}
          />
        ))}
        
        <RespondentInfo 
          info={respondentInfo}
          onChange={handleRespondentInfoChange}
        />
        
        <FormActions 
          submitting={submitting}
        />
      </form>
    </div>
  );
};

export default FillSurvey;