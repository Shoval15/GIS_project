import React from 'react';
import './styles/LanguageSwitch.css'; 

const LanguageSwitch = ({ language, toggleLanguage }) => {
  return (
    <div className="language-switch">
      <span 
        onClick={toggleLanguage}
        className="flag-icon"
        role="button"
        aria-label={`Switch to ${language === 'he' ? 'Hebrew' : 'English'}`}
        tabIndex="0"
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') toggleLanguage(); }}
      >
        {language === 'he' ? <img src="usa-flag.png" alt="USA Flag" className='img-flag' style={{width:'30px'}}/> : <img src="israel-flag.png" alt="Israel Flag" className='img-flag' style={{width:'30px'}}/> }
      </span>
    </div>
  );
};

export default LanguageSwitch;
