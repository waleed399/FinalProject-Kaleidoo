// src/components/MenuBar.js

import React from 'react';
import { Link } from 'react-router-dom'; // If using react-router for navigation
import '../styling/MenuBar.css'; // Ensure you create this CSS file

const MenuBar = () => {
  return (
    <div className="menu-bar">
      <Link to="/">Home</Link>
      <Link to="/contact">Contact Us</Link>
      {/* Add more links as needed */}
      <div className="search-bar">
        <input type="text" placeholder="Search products..." />
        <button>Search</button>
      </div>
    </div>
  );
};

export default MenuBar;
