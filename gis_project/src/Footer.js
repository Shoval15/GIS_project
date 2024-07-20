import React from 'react';
import { projectName } from './names';
import './styles/Footer.css';

function Footer() {
  // Split the project name into parts
  const parts = projectName.split('Green');

  return (
    <div className="footer-container">
      <img
        src="logo.png"
        className="footer-image"
        alt="Logo"
      />
      <div className="footer-overlay" />
      <h1 className="footer-title">
        Shoval Aharon - {parts[0]}
        <span style={{color: '#548762'}}>GREEN</span>
        {parts[1]}
      </h1>
    </div>
  );
}

export default Footer;