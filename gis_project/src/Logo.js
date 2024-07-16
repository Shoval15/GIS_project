import React from 'react';
import { projectName } from './names';

const styles = {
  container: {
    position: 'relative',
    width: '100vw',
    height: '30vh',
    overflow: 'hidden',
    borderRadius: '15px'
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
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
  },
  titleContainer: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    textAlign: 'center',
  },
  title: {
    color: 'white',
    textShadow: '2px 2px 4px rgba(0,0,0,0.7)',
    fontFamily: "'Montserrat', sans-serif",
    fontSize: '3.5rem',
    fontWeight: 700,
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
    margin: 0,
    padding: '10px 20px',
    border: '3px solid white',
    borderRadius: '10px',
    backdropFilter: 'blur(5px)'
  },
  explanation: {
    color: 'white',
    fontFamily: "'Montserrat', sans-serif",
    fontSize: '1.2rem',
    marginTop: '10px',
    textShadow: '1px 1px 2px rgba(0,0,0,0.7)',
  }
};

function Logo() {
  return (
    <div style={styles.container}>
      <img
        src="logo.png"
        style={styles.image}
        alt="Logo"
      />
      <div style={styles.overlay} />
      <div style={styles.titleContainer}>
        <h1 style={styles.title}>
          {projectName}
        </h1>
        <h3 style={styles.explanation}>הסבר</h3>
      </div>
    </div>
  );
}

export default Logo;