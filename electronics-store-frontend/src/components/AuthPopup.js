import React, { useState } from 'react';
import axios from 'axios';
import '../styling/AuthPopup.css';

const AuthPopup = ({ onClose, onLoginSuccess }) => {
  const [isRegister, setIsRegister] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');

  const handleRegister = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5555/api/register', {
        username,
        password,
        email
      });
      alert(response.data.message);
      onClose();
    } catch (error) {
      alert(error.response.data.error);
    }
  };

  const handleLogin = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5555/api/login', {
        username,
        password
      });
      alert(response.data.message);
      onLoginSuccess(username);  // Call the onLoginSuccess prop with the username
      onClose();
    } catch (error) {
      alert(error.response.data.error);
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
        <button onClick={isRegister ? handleRegister : handleLogin}>
          {isRegister ? 'Register' : 'Login'}
        </button>
        <p onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
        </p>
      </div>
    </div>
  );
};

export default AuthPopup;
