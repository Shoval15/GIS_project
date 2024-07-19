import React from 'react';
import { strings } from './strings';
function ResultsDisplay({ results, language }) {
  const resultsContainer = {
    width: '100%',
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '10px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    // direction: 'rtl', // Right-to-left direction for Hebrew
  };

  const statItem = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 0',
    borderBottom: '1px solid #dee2e6',
  };

  const statLabel = {
    fontWeight: 'bold',
    color: '#495057',
  };

  const statValue = {
    fontSize: '1.2em',
    color: '#212529',
  };

  const progressBarContainer = {
    width: '100%',
    backgroundColor: '#e9ecef',
    borderRadius: '5px',
    marginTop: '10px',
  };

  const progressBar = {
    width: `${results.allocation_percentage}%`,
    height: '20px',
    backgroundColor: '#28a745',
    borderRadius: '5px',
    transition: 'width 0.5s ease-in-out',
  };

  return (
    <div style={resultsContainer}>
      <h3 style={{ marginBottom: '20px', color: '#343a40' }}>{strings.results[language]}</h3>
      {results ? (
        <>
          <div style={statItem}>
            <span style={statLabel}>{strings.totalApartments[language]}:</span>
            <span style={statValue}>{results.total_apartments}</span>
          </div>
          <div style={statItem}>
            <span style={statLabel}>{strings.allocatedApartments[language]}:</span>
            <span style={statValue}>{results.allocated_apartments}</span>
          </div>
          <div style={statItem}>
            <span style={statLabel}>{strings.notAllocatedApartments[language]}:</span>
            <span style={statValue}>{results.not_allocated_apartments}</span>
          </div>
          <div style={statItem}>
            <span style={statLabel}>{strings.allocationPercentage[language]}:</span>
            <span style={statValue}>{results.allocation_percentage.toFixed(2)}%</span>
          </div>
          <div style={progressBarContainer}>
            <div style={progressBar} title={`${results.allocation_percentage.toFixed(2)}%`}></div>
          </div>
        </>
      ) : (
        <p>{strings.noResults[language]}</p>
      )}
    </div>
  );
}

export default ResultsDisplay;