import React from 'react';
import { Link } from 'react-router-dom';
import '../styling/ProductItem.css';
import imageMapping from '../imageMapping'; // Updated import path

function ProductItem({ product, loggedInUser, onProductClick, onPurchaseClick }) {
  // Use the product name to get the correct image URL from the mapping
  const imageUrl = `${process.env.PUBLIC_URL}/images/${imageMapping[product.name.replace(/\//g, ':')] || 'placeholder.jpg'}`;

  const handleClick = () => {
    console.log("ProductItem handleClick triggered");
    if (loggedInUser && onProductClick) {
      console.log(`Triggering onProductClick with product ID: ${product.id}`);
      onProductClick(product.id); // Call the click handler with product ID
    }
  };

  const handlePurchase = (e) => {
    e.stopPropagation(); // Prevent the click event from propagating to the parent
    console.log("ProductItem handlePurchase triggered");
    if (loggedInUser && onPurchaseClick) {
      console.log(`Triggering onPurchaseClick with product ID: ${product.id}`);
      onPurchaseClick(product.id); // Call the purchase handler with product ID
    }
  };

  return (
    <div className="product-item" onClick={handleClick}>
      <Link to={`/product/${product.id}`} state={{ loggedInUser }}>
        <img src={imageUrl} alt={product.name} />
        <h2>{product.name}</h2>
      </Link>
      <button onClick={handlePurchase}>Purchase</button> {/* Add a Purchase button */}
    </div>
  );
}

export default ProductItem;
