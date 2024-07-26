import React, { useEffect, useState } from 'react';
import Button from 'react-bootstrap/Button';
import { strings } from './strings';
import './styles/SideMenu.css';

function SideMenu({handleSend, bounds, language, loading}) {
  const [formData, setFormData] = useState({
    projectStatus: '',
    apartmentType: 'existing',
    distance: '0.93',
    sqMeterPerResident: '3',
    residentsPerApartment: '3.5'
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
  useEffect(()=> {
    
  },[loading]);

  return (
    <div className={`side-menu ${language === 'he' ? 'rtl-text' : 'ltr-text'}`}>
      {/* <img src="logo.png" alt="Logo" className="side-menu-logo" /> */}
      <form className="side-menu-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">{strings.apartmentType[language]}:</label>
          <div className="radio-group">
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
          <div className="radio-group">
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
          <div className="form-group">
            <label htmlFor="projectStatus" className="form-label">{strings.projectStatus[language]}:</label>
            <select 
              id="projectStatus" 
              name="projectStatus"
              className="form-select"
              value={formData.projectStatus}
              onChange={handleChange}
            >
              <option value="">{strings.chooseStatus[language]}</option>
              <option value={`פתיחת תיק תב"ע`}>{strings.urbanPlanFileOpened[language]}</option>
              <option value="הפקדה">{strings.deposit[language]}</option>
              <option value="תכנית מאושרת">{strings.approvedPlan[language]}</option>
              <option value="נפתח תיק היתר">{strings.permitFileOpened[language]}</option>
              <option value="היתר בנייה">{strings.buildingPermit[language]}</option>
            </select>
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="distance" className="form-label">{strings.maxDistanceBuildingToGarden[language]}:</label>
          <div className="input-group col-md-6">
            <input 
              type="number" 
              id="distance" 
              name="distance"
              className="form-input"
              value={formData.distance}
              onChange={handleChange}
              step="0.01"
              min="0"
            />
            <span className="input-label">{strings.km[language]}</span>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="sqMeterPerResident" className="form-label">
            {strings.sqMeterPerResident[language]}:
          </label>
          <div className="input-group col-md-6">
            <input 
              type="number" 
              id="sqMeterPerResident" 
              name="sqMeterPerResident"
              className="form-input"
              value={formData.sqMeterPerResident}
              onChange={handleChange}
              step="0.1"
              min="0.5"
            />
            <span className="input-label">{strings.sqm[language]}</span>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="residentsPerApartment" className="form-label">
            {strings.residentsPerApartment[language]}:
          </label>
          <div className="input-group col-md-6">
            <input 
              type="number" 
              id="residentsPerApartment" 
              name="residentsPerApartment"
              className="form-input"
              value={formData.residentsPerApartment}
              onChange={handleChange}
              step="0.5"
              min="1"
            />
          </div>
        </div>
        {!bounds && (
          <label className="blinking-label">{strings.drawBoundsPrompt[language]}</label>
        )}
        {bounds && !loading &&(
          <Button variant="outline-success" type="submit">{strings.send[language]}</Button>
        )}
        {loading && (
        <img src="loading.gif" alt="loading"></img>

        )}
      </form>
    </div>
  );
}

export default SideMenu;