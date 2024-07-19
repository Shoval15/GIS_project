import React, { useState } from 'react';
import { Container, Navbar } from 'react-bootstrap';
import Logo from './Logo';
import Map from './Map';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Footer from './Footer';
import LanguageSwitch from './LanguageSwitch'; // Import the custom LanguageSwitch component

export const debugging_be = "http://127.0.0.1:5000/";
export const deploy_be = "https://finalproject-3bd85.web.app/";

function App() {
  const [language, setLanguage] = useState('he');

  const toggleLanguage = () => {
    console.log(language)
    setLanguage(prevLang => (prevLang === 'en' ? 'he' : 'en'));
  };

  return (
    <div className="App">
    <Logo language={language} toggleLanguage={toggleLanguage}/>
    <br></br>
    <Map language={language}/>
    <br></br>
    <Footer language={language} />
</div>
  );
}

export default App;
