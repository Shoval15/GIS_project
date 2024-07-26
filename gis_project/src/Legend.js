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
          <div className="legend-color legend-color-multi"></div>
          <span>{strings.buildingsAndAssignedGardens[language]}</span>
        </div>
        <div className="legend-item">
          <div className="legend-color legend-color-red"></div>
          <span>{strings.buildingsWithoutAssignedGarden[language]}</span>
        </div>
        <div className="legend-item">
          <div className="legend-color legend-color-green-border"></div>
          <span>{strings.gardenBorder[language]}</span>
        </div>
      </Card.Body>
    </Card>
  );
};

export default Legend;