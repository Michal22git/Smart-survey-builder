import React from 'react';
import { Link } from 'react-router-dom';

const NavigationBar = () => {
  return (
    <header>
      <nav className="navbar">
        <div className="navbar-container">
          <Link to="/" className="navbar-logo">
            Smart Survey Builder
          </Link>
        </div>
      </nav>
    </header>
  );
};

export default NavigationBar;
