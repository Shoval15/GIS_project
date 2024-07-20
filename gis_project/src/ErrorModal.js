import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import { strings } from './strings';
import './styles/ErrorModal.css';

function ErrorModal({ show, onHide, message, language }) {
  const rtlClass = language === 'he' ? 'rtl' : '';

  return (
    <Modal show={show} onHide={onHide} centered className={rtlClass}>
      <Modal.Header closeButton>
        <Modal.Title>{strings['error'][language]}</Modal.Title>
      </Modal.Header>
      <Modal.Body>{message}</Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          {strings['close'][language]}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default ErrorModal;