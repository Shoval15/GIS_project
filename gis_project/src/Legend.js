import React from 'react';
import { Card } from 'react-bootstrap';
import './App.css';
import { strings } from './strings';

const Legend = ({ language }) => {
  return (
    <Card style={{ 
      width: '200px', 
      position: 'absolute', 
      bottom: '10px', 
      left: '10px', 
      zIndex: 1000,
      direction: language === 'he' ? 'rtl' : 'ltr'
    }}>
      <Card.Body>
        <Card.Title>{strings.legend[language]}</Card.Title>
        <div>
          <div style={{ backgroundColor: 'blue', width: '20px', height: '20px', display: 'inline-block', marginInlineEnd: '5px' }}></div>
          <span>{strings.buildingsWithAssignedGarden[language]}</span>
        </div>
        <div>
          <div style={{ backgroundColor: 'red', width: '20px', height: '20px', display: 'inline-block', marginInlineEnd: '5px' }}></div>
          <span>{strings.buildingsWithoutAssignedGarden[language]}</span>
        </div>
        <div>
          <div style={{ backgroundColor: 'green', width: '20px', height: '20px', display: 'inline-block', marginInlineEnd: '5px' }}></div>
          <span>{strings.garden[language]}</span>
        </div>
      </Card.Body>
    </Card>
  );
};

export default Legend;