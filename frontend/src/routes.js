import React from 'react';
import { Routes, Route } from 'react-router-dom';
import CreateSurvey from './components/CreateSurvey/CreateSurvey';
import SurveyList from './components/SurveyList/SurveyList';
import FillSurvey from './components/FillSurvey/FillSurvey';

// Dodaj konsolę do testowania
console.log('Routes loaded, FillSurvey component:', FillSurvey);

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<SurveyList />} />
      <Route path="/create" element={<CreateSurvey />} />
      <Route path="/surveys/:publicId/fill" element={<FillSurvey />} />
    </Routes>
  );
};

export default AppRoutes; 