import React, { useState, useRef, useEffect } from 'react';


function ResultsDisplay({results}) {

  const resultsContainer = {
    width: '100%',
    height: '100%',
    padding: '15px',
    backgroundColor: '#f5f5f5',
    borderRadius: '15px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    overflowY: 'auto'
};
  return (
    <div style={resultsContainer}>
      <h3>Results</h3>
      {results ? (
        <pre>{JSON.stringify(results, null, 2)}</pre>
      ) : (
        <p>No results to display yet.</p>
      )}
    </div>
  );
}

export default ResultsDisplay;