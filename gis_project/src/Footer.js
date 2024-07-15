import React from 'react';
import { projectName } from './names';
const styles = {
  container: {
    position: 'relative',
    width: '100vw',
    height: '3vh',
    overflow: 'hidden',
    borderRadius: '5px'
  },
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    
  },
  title: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    color: 'white',
    textShadow: '2px 2px 4px rgba(0,0,0,0.7)',
    fontFamily: "'Montserrat', sans-serif",
    fontSize: '9px',
    fontWeight: 700,
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
    margin: 0,
    padding: '10px 20px',
    borderRadius: '10px',
    backdropFilter: 'blur(5px)'
  }
};

function Footer() {
  return (
    <div style={styles.container}>
      <img
        src="logo.png"
        style={styles.image}
        alt="Logo"
      />
      <div style={styles.overlay} />
      <h1 style={styles.title}>
        Shoval Aharon - { projectName }
      </h1>
    </div>
  );
}

export default Footer;