import React from 'react';
import { strings } from '../utilities/strings';
import '../styles/ResultsDisplay.css';
import { ProgressBar } from 'react-bootstrap';

function ResultsDisplay({ results, language }) {
  return (
    <div className={`results-container ${language === 'he' ? 'rtl-text' : 'ltr-text'}`} >
      <h3 className="results-title">{strings.results[language]}</h3>
      
      {results ? (
        <>
          <h4>{strings.apartmentStats[language]}</h4>
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
            <span className="stat-label">{strings.apartmentAllocationPercentage[language]}:</span>
            <span className="stat-value">{results.apartment_allocation_percentage.toFixed(2)}%</span>
          </div>
          <ProgressBar 
            variant="info"
            now={results.apartment_allocation_percentage}
            label={`${results.apartment_allocation_percentage.toFixed(2)}%`}
          />

          <h4>{strings.buildingStats[language]}</h4>
          <div className="stat-item">
            <span className="stat-label">{strings.totalBuildings[language]}:</span>
            <span className="stat-value">{results.total_buildings}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">{strings.allocatedBuildings[language]}:</span>
            <span className="stat-value">{results.allocated_buildings}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">{strings.notAllocatedBuildings[language]}:</span>
            <span className="stat-value">{results.not_allocated_buildings}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">{strings.buildingAllocationPercentage[language]}:</span>
            <span className="stat-value">{results.building_allocation_percentage.toFixed(2)}%</span>
          </div>
          <ProgressBar 
            variant="success"
            now={results.building_allocation_percentage}
            label={`${results.building_allocation_percentage.toFixed(2)}%`}
          />
        </>
      ) : (
        <p>{strings.noResults[language]}</p>
      )}
    </div>
  );
}

export default ResultsDisplay;