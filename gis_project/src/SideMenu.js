import React, { useState } from 'react';
import './App.css';
import Button from 'react-bootstrap/Button';


const styles = {
  sideMenu: {
    position: 'absolute',
    top: 0,
    left: 0,
    height: '100%',
    width: '300px',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    boxShadow: '2px 0 5px rgba(0, 0, 0, 0.1)',
    zIndex: 1000,
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center', 
    borderRadius: '15px',
    direction: 'rtl'
  },
  logo: {
    width: '100%',
    marginBottom: '20px',
    textAlign: 'center',
    borderRadius: '15px',

  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    alignItems: 'center', 
    width: '100%', 
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
    alignItems: 'center', 
    width: '100%', 
  },
  label: {
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center', 
  },
  select: {
    padding: '5px',
    borderRadius: '5px',
    border: '1px solid #ccc',
    width: '100%',
    textAlign: 'center', 
  },
  radio: {
    margin: '5px 0',
    display: 'flex',
    justifyContent: 'center',
    width: '100%',
  },
  input: {
    padding: '5px',
    borderRadius: '5px',
    border: '1px solid #ccc',
    width: 'calc(100% - 40px)',
    textAlign: 'center',
  },
  inputGroup: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  inputLabel: {
    marginLeft: '5px',
    color: '#666',
  },
  blinkingLabel: {
    animation: 'blink 1.5s linear infinite',
    fontWeight: 'bold',
  },
};


function SideMenu({handleSend, bounds}) {
  const [formData, setFormData] = useState({
    projectStatus: '',
    apartmentType: 'existing',
    distance: '0.93'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (bounds) {
      handleSend(formData);
    } else {
      alert('יש לצייר תחום מבוקש על המפה');
    }
  };

  return (
    <div style={styles.sideMenu}>
      <img src="img2.jpeg" alt="Logo" style={styles.logo} />
      <form style={styles.form} onSubmit={handleSubmit}>
        <div style={styles.formGroup}>
          <label style={styles.label}>סוג דירות:</label>
          <div style={styles.radio}>
            <input 
              type="radio" 
              id="existing" 
              name="apartmentType" 
              value="existing"
              checked={formData.apartmentType === 'existing'}
              onChange={handleChange}
            />
            <label htmlFor="existing">קיימות</label>
          </div>
          <div style={styles.radio}>
            <input 
              type="radio" 
              id="proposed" 
              name="apartmentType" 
              value="proposed"
              checked={formData.apartmentType === 'proposed'}
              onChange={handleChange}
            />
            <label htmlFor="proposed">מוצעות</label>
          </div>
        </div>
        {formData.apartmentType === 'proposed' && (
          <div style={styles.formGroup} >
            <label htmlFor="projectStatus" style={styles.label}>סטטוס פרויקט:</label>
            <select 
              id="projectStatus" 
              name="projectStatus"
              style={styles.select}
              value={formData.projectStatus}
              onChange={handleChange}
            >
              <option value="">בחר סטטוס</option>
              <option value="א">א</option>
              <option value="ב">ב</option>
              <option value="ג">ג</option>
              <option value="ד">ד</option>
            </select>
          </div>
        )}
        
        <div style={styles.formGroup} >
          <label htmlFor="distance" style={styles.label}>מרחק מקסימלי בין בניין לשצ"פ:</label>
          <div style={styles.inputGroup} className='col-md-6'>
            <input 
              type="number" 
              id="distance" 
              name="distance"
              style={styles.input}
              value={formData.distance}
              onChange={handleChange}
              step="0.01"
              min="0"
            />
            <span style={styles.inputLabel}>ק"מ</span>
          </div>
        </div>
        {!bounds && (
          <label style={styles.blinkingLabel}>יש לצייר תחום מבוקש על המפה</label>
        )}
        {bounds && (
        <Button variant="outline-success" type="submit" >שלח</Button>

        )}
      </form>
    </div>
  );
}

export default SideMenu;