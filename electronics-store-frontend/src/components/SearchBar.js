import React from 'react';

function SearchBar({ onSearch }) {
  return (
    <input
      type="text"
      placeholder="Search products..."
      onChange={(e) => onSearch(e.target.value)}
    />
  );
}

export default SearchBar;