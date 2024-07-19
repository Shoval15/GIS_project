import React from 'react';
import './App.css'; 

const LanguageSwitch = ({ language, toggleLanguage }) => {
  return (
    <div className="language-switch">
      <label className="switch">
        <input
          type="checkbox"
          checked={language === 'en'}
          onChange={toggleLanguage}
        />
        <span className="slider round"></span>
      </label>
      <span className="language-label" style={{color:'white'}}>
        {language === 'en' ? 'EN' : 'עב'}
      </span>
    </div>
  );
};

export default LanguageSwitch;