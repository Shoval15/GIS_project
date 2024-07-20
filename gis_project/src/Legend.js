import React from 'react';
import { Card } from 'react-bootstrap';
import './styles/Legend.css';
import { strings } from './strings';

const Legend = ({ language }) => {
  return (
    <Card className={`legend-card ${language === 'he' ? 'rtl' : 'ltr'}`}>
      <Card.Body>
        <Card.Title>{strings.legend[language]}</Card.Title>
        <div className="legend-item">
          <div className="legend-color legend-color-blue"></div>
          <span>{strings.buildingsWithAssignedGarden[language]}</span>
        </div>
        <div className="legend-item">
          <div className="legend-color legend-color-red"></div>
          <span>{strings.buildingsWithoutAssignedGarden[language]}</span>
        </div>
        <div className="legend-item">
          <div className="legend-color legend-color-green"></div>
          <span>{strings.garden[language]}</span>
        </div>
      </Card.Body>
    </Card>
  );
};

export default Legend;