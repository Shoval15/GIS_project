import React from 'react';
import { projectName } from './names';
import LanguageSwitch from './LanguageSwitch';
import './styles/Logo.css';
import { strings } from './strings';

function Logo({language, toggleLanguage}) {
  // Split the project name into parts
  const parts = projectName.split('Green');
  console.log(parts)

  return (
    <div className="logo-container">
      <img
        src="logo.png"
        className="logo-image"
        alt="Logo"
      />
      <div className="logo-overlay" />

      <div className="language-switch-container">
        <LanguageSwitch language={language} toggleLanguage={toggleLanguage} />
      </div>

      <div className="logo-title-container">
        <h1 className="logo-title">
          {parts[0]}
          <span style={{color: '#548762'}}>GREEN</span>
          {parts[1]}
        </h1>
        <h3 className="logo-explanation">{strings['explanation'][language]}</h3>
      </div>
    </div>
  );
}

export default Logo;