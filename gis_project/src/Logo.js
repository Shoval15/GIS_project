import React from 'react';
import { projectName } from './names';
import LanguageSwitch from './LanguageSwitch';
import './styles/Logo.css';

function Logo({language, toggleLanguage}) {
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
          {projectName}
        </h1>
        <h3 className="logo-explanation">הסבר</h3>
      </div>
    </div>
  );
}

export default Logo;