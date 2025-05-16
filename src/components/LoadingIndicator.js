import React from 'react';
import './LoadingIndicator.css';

const LoadingIndicator = ({ message = 'Loading...' }) => {
  return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p className="loading-text">{message}</p>
    </div>
  );
};

export default LoadingIndicator; 