import React, { useState } from 'react';
import './App.css';
import Button from 'react-bootstrap/Button';
import { strings } from './strings';

const styles = {
  sideMenu: {
    top: 0,
    right: 0,
    height: '100%',
    width: '300px',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    boxShadow: '2px 0 5px rgba(0, 0, 0, 0.1)',
    zIndex: 1000,
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center', 
    borderRadius: '15px',
    direction: 'rtl'
  },
  logo: {
    width: '100%',
    marginBottom: '20px',
    textAlign: 'center',
    borderRadius: '15px',

  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    alignItems: 'center', 
    width: '100%', 
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
    alignItems: 'center', 
    width: '100%', 
  },
  label: {
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center', 
  },
  select: {
    padding: '5px',
    borderRadius: '5px',
    border: '1px solid #ccc',
    width: '100%',
    textAlign: 'center', 
  },
  radio: {
    margin: '5px 0',
    display: 'flex',
    justifyContent: 'center',
    width: '100%',
  },
  input: {
    padding: '5px',
    borderRadius: '5px',
    border: '1px solid #ccc',
    width: 'calc(100% - 40px)',
    textAlign: 'center',
  },
  inputGroup: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  inputLabel: {
    marginLeft: '5px',
    color: '#666',
  },
  blinkingLabel: {
    animation: 'blink 1.5s linear infinite',
    fontWeight: 'bold',
  },
};


function SideMenu({handleSend, bounds, language}) {
  const [formData, setFormData] = useState({
    projectStatus: '',
    apartmentType: 'existing',
    distance: '0.93'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (bounds) {
      handleSend(formData);
    } else {
      alert(strings.drawBoundsAlert[language]);
    }
  };

  return (
    <div style={{...styles.sideMenu, direction: language === 'he' ? 'rtl' : 'ltr'}}>
      <img src="img2.jpeg" alt="Logo" style={styles.logo} />
      <form style={styles.form} onSubmit={handleSubmit}>
        <div style={styles.formGroup}>
          <label style={styles.label}>{strings.apartmentType[language]}:</label>
          <div style={styles.radio}>
            <input 
              type="radio" 
              id="existing" 
              name="apartmentType" 
              value="existing"
              checked={formData.apartmentType === 'existing'}
              onChange={handleChange}
            />
            <label htmlFor="existing">{strings.existing[language]}</label>
          </div>
          <div style={styles.radio}>
            <input 
              type="radio" 
              id="proposed" 
              name="apartmentType" 
              value="proposed"
              checked={formData.apartmentType === 'proposed'}
              onChange={handleChange}
            />
            <label htmlFor="proposed">{strings.existingAndProposed[language]}</label>
          </div>
        </div>
        {formData.apartmentType === 'proposed' && (
          <div style={styles.formGroup} >
            <label htmlFor="projectStatus" style={styles.label}>{strings.projectStatus[language]}:</label>
            <select 
              id="projectStatus" 
              name="projectStatus"
              style={styles.select}
              value={formData.projectStatus}
              onChange={handleChange}
            >
              <option value="">{strings.chooseStatus[language]}</option>
              <option value="היתר בניה">{strings.buildingPermit[language]}</option>
              <option value="נפתח תיק היתר">{strings.permitFileOpened[language]}</option>
              <option value="תכנית מאושרת">{strings.approvedPlan[language]}</option>
              <option value="הפקדה">{strings.deposit[language]}</option>
              <option value="פתיחת תיק תבע">{strings.urbanPlanFileOpened[language]}</option>
            </select>
          </div>
        )}
        
        <div style={styles.formGroup} >
          <label htmlFor="distance" style={styles.label}>{strings.maxDistanceBuildingToGarden[language]}:</label>
          <div style={styles.inputGroup} className='col-md-6'>
            <input 
              type="number" 
              id="distance" 
              name="distance"
              style={styles.input}
              value={formData.distance}
              onChange={handleChange}
              step="0.01"
              min="0"
            />
            <span style={styles.inputLabel}>{strings.km[language]}</span>
          </div>
        </div>
        {!bounds && (
          <label style={styles.blinkingLabel}>{strings.drawBoundsPrompt[language]}</label>
        )}
        {bounds && (
          <Button variant="outline-success" type="submit">{strings.send[language]}</Button>
        )}
      </form>
    </div>
  );
}

export default SideMenu;