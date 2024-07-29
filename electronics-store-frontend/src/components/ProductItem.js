import React from 'react';
import { Link } from 'react-router-dom';
import '../styling/ProductItem.css';
import imageMapping from '../../src/imageMapping';  // Update the import path

function ProductItem({ product, loggedInUser }) {
  // Use the product name to get the correct image URL from the mapping
  const imageUrl = `${process.env.PUBLIC_URL}/images/${imageMapping[product.name.replace(/\//g, ':')]}`;
  
  return (
    <div className="product-item">
      <Link to={`/product/${product.id}`} state={{ loggedInUser }}>
        <img src={imageUrl} alt={product.name} />
        <h2>{product.name}</h2>
      </Link>
    </div>
  );
}

export default ProductItem;
