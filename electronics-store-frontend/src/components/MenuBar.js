import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styling/MenuBar.css';

const MenuBar = ({ onSearch, onReset, loggedInUser, onAuthClick, onLogout }) => {
  const [searchInput, setSearchInput] = useState('');

  const handleSearchChange = (event) => {
    setSearchInput(event.target.value);
  };

  const handleSearchClick = () => {
    onSearch(searchInput);
  };

  const handleHomeClick = () => {
    setSearchInput('');
    onReset(); // Just reset the state, do not perform a search
  };

  return (
    <div className="menu-bar">
      <Link to="/" onClick={handleHomeClick}>Home</Link>
      <Link to="/contact">Contact Us</Link>
      <div className="search-bar">
        <input 
          type="text" 
          value={searchInput} 
          onChange={handleSearchChange} 
          placeholder="Search products..."
        />
        <button onClick={handleSearchClick}>Search</button>
      </div>
      {loggedInUser ? (
        <div className="auth-section">
          <span className="welcome-message">Welcome, {loggedInUser}</span>
          <button onClick={onLogout} className="logout-button">Logout</button>
        </div>
      ) : (
        <button onClick={onAuthClick} className="auth-button">Login/Register</button>
      )}
    </div>
  );
};

export default MenuBar;
