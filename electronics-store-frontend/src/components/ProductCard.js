import React from 'react';
import '../styling/ProductCard.css';
import imageMapping from '../../src/imageMapping';  // Update the import path

function ProductCard({ name }) {
  // Use the product name to get the correct image URL from the mapping
  const imageUrl = `${process.env.PUBLIC_URL}/images/${imageMapping[name]}`;
  
  return (
    <div className="product-card">
      <img src={imageUrl} alt={name} />
      <h3>{name}</h3>
    </div>
  );
}

export default ProductCard;
