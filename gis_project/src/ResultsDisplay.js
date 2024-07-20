import React from 'react';
import { strings } from './strings';
import './styles/ResultsDisplay.css';
import { ProgressBar } from 'react-bootstrap';

function ResultsDisplay({ results, language }) {
  return (
    <div className={`results-container ${language === 'he' ? 'rtl-text' : 'ltr-text'}`} >
      <h3 className="results-title">{strings.results[language]}</h3>
      
      {results ? (
        <>
          <div className="stat-item">
            <span className="stat-label">{strings.totalApartments[language]}:</span>
            <span className="stat-value">{results.total_apartments}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">{strings.allocatedApartments[language]}:</span>
            <span className="stat-value">{results.allocated_apartments}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">{strings.notAllocatedApartments[language]}:</span>
            <span className="stat-value">{results.not_allocated_apartments}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">{strings.allocationPercentage[language]}:</span>
            <span className="stat-value">{results.allocation_percentage.toFixed(2)}%</span>
          </div>
          <ProgressBar 
          variant="info"
          now={results.allocation_percentage}
          label={`${results.allocation_percentage.toFixed(2)}%`}
          />
        </>
      ) : (
        <p>{strings.noResults[language]}</p>
      )}
    </div>
  );
}

export default ResultsDisplay;