// src/components/SearchBar.js

import React, { useState } from 'react';
import '../styling/SearchBar.css'; // Ensure you have this CSS file

const SearchBar = ({ onSearch }) => {
  const [searchInput, setSearchInput] = useState('');

  const handleSearchChange = (event) => {
    setSearchInput(event.target.value);
    onSearch(event.target.value); // Pass the search term to the parent component
  };

  const handleSearchClick = () => {
    onSearch(searchInput); // Trigger search when button is clicked
  };

  return (
    <div className="search-bar">
      <input 
        type="text" 
        value={searchInput} 
        onChange={handleSearchChange} 
        placeholder="Search products..."
      />
      <button onClick={handleSearchClick}>Search</button>
    </div>
  );
};

export default SearchBar;
