import React from 'react';
import { Link } from 'react-router-dom';
import '../styling/ProductItem.css';
import imageMapping from '../imageMapping'; // Updated import path

function ProductItem({ product, loggedInUser, onProductClick }) {
  // Use the product name to get the correct image URL from the mapping
  const imageUrl = `${process.env.PUBLIC_URL}/images/${imageMapping[product.name.replace(/\//g, ':')] || 'placeholder.jpg'}`;

  const handleClick = () => {
    console.log("ProductItem handleClick triggered");
    if (loggedInUser && onProductClick) {
      console.log(`Triggering onProductClick with product ID: ${product.id}`);
      onProductClick(product.id); // Call the click handler with product ID
    }
  };
  

  return (
    <div className="product-item" onClick={handleClick}>
      <Link to={`/product/${product.id}`} state={{ loggedInUser }}>
        <img src={imageUrl} alt={product.name} />
        <h2>{product.name}</h2>
      </Link>
    </div>
  );
}

export default ProductItem;
