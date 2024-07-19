import React from 'react';
import { Container, Navbar } from 'react-bootstrap';
import Logo from './Logo';
import Map from './Map';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Footer from './Footer';

export const debugging_be = "http://127.0.0.1:5000/";
export const deploy_be = "https://finalproject-3bd85.web.app/";
function App() {
  return (
    <div className="App">
        <Logo />
        <br></br>
        <Map />
        <br></br>
        <Footer />
    </div>
  );
}

export default App;