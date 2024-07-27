import React, { useState } from 'react';
import Logo from './Layout/Logo';
import Map from './MapPage/Map';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/App.css';
import Footer from './Layout/Footer';

export const debugging_be = "http://127.0.0.1:5000/";
export const deploy_be = "https://finalproject-3bd85.web.app/";

function App() {
  const [language, setLanguage] = useState('he');

  const toggleLanguage = () => {
    console.log(language)
    setLanguage(prevLang => (prevLang === 'en' ? 'he' : 'en'));
  };
  const appClassName = `App ${language === 'he' ? 'rtl' : 'ltr'}`;


  return (
    <div className={appClassName}>
    <Logo language={language} toggleLanguage={toggleLanguage}/>
    <br></br>
    <Map language={language}/>
    <Footer language={language} />
</div>
  );
}

export default App;
