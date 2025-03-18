import React from 'react';
import { BrowserRouter as Router, Link } from 'react-router-dom';
import './App.css';
import AppRoutes from './routes';

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
          <AppRoutes />
        </main>
      </div>
    </Router>
  );
}

export default App;