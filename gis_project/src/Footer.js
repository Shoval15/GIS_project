import React from 'react';
import { projectName } from './names';
import './styles/Footer.css';

function Footer() {
  return (
    <div className="footer-container">
      <img
        src="logo.png"
        className="footer-image"
        alt="Logo"
      />
      <div className="footer-overlay" />
      <h1 className="footer-title">
        Shoval Aharon - {projectName}
      </h1>
    </div>
  );
}

export default Footer;