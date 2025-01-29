import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import SurveyList from './components/SurveyList/SurveyList';
import CreateSurvey from './components/CreateSurvey/CreateSurvey';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">Smart Survey Builder</div>
          <div className="nav-links">
            <Link to="/">Surveys</Link>
            <Link to="/create">Create Survey</Link>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<SurveyList />} />
            <Route path="/create" element={<CreateSurvey />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
