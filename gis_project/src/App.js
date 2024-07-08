import React from 'react';
import { Container, Navbar } from 'react-bootstrap';
import Logo from './Logo';
import Map from './Map';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <div className="App">
      <Navbar bg="light">
        <Container>
          <Navbar.Brand>
            <Logo />
            My GIS project
          </Navbar.Brand>
        </Container>
      </Navbar>
      <Container className="mt-3">
        <Map />
      </Container>
    </div>
  );
}

export default App;