import React, { useState } from 'react';
import axios from 'axios';
import '../styling/AuthPopup.css';
import NotificationPopup from './NotificationPopup';

const AuthPopup = ({ onClose, onLoginSuccess }) => {
  const [isRegister, setIsRegister] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Manage loading state

  const handleRegister = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5555/api/register', {
        username,
        password,
        email
      });
      setPopupMessage(response.data.message);
      setShowPopup(true);
      setIsLoading(false);
      setTimeout(() => {
        setShowPopup(false);
        onClose(); // Close the popup and then call onClose to handle any additional logic
      }, 2000);
    } catch (error) {
      setPopupMessage(error.response ? error.response.data.error : 'An error occurred');
      setShowPopup(true);
      setIsLoading(false);
    }
  };

  const handleLogin = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5555/api/login', {
        username,
        password
      });
      setPopupMessage(response.data.message);
      setShowPopup(true);
      setIsLoading(false);
      setTimeout(() => {
        setShowPopup(false);
        onLoginSuccess(username); // Call onLoginSuccess after popup is closed
        onClose(); // Close the popup and then navigate
      }, 2000);
    } catch (error) {
      setPopupMessage(error.response ? error.response.data.error : 'An error occurred');
      setShowPopup(true);
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-popup">
      <div className="auth-popup-content">
        <span className="auth-popup-close" onClick={onClose}>&times;</span>
        <h2>{isRegister ? 'Register' : 'Login'}</h2>
        <input 
          type="text" 
          placeholder="Username" 
          value={username} 
          onChange={(e) => setUsername(e.target.value)} 
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
        />
        {isRegister && (
          <input 
            type="email" 
            placeholder="Email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
          />
        )}
        <button onClick={isRegister ? handleRegister : handleLogin} disabled={isLoading}>
          {isRegister ? 'Register' : 'Login'}
        </button>
        <p onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
        </p>
      </div>

      {/* Conditionally render the NotificationPopup */}
      {showPopup && (
        <NotificationPopup
          message={popupMessage}
          onClose={() => setShowPopup(false)}
        />
      )}
    </div>
  );
};

export default AuthPopup;
