import React from 'react';
import '../styling/ProductCard.css';
import imageMapping from '../../src/imageMapping';  // Update the import path

function ProductCard({ products, onProductClick }) {
  // Create a set to track unique names
  const uniqueProducts = Array.from(
    new Map(products.map(product => [product.name, product])).values()
  );

  const handleClick = (productId) => {
    if (onProductClick) {
      onProductClick(productId); // Call the click handler with product ID
    }
  };

  return (
    <div className="product-card-container">
      {uniqueProducts.map(product => {
        // Ensure the product name matches the keys in imageMapping
        const imageUrl = `${process.env.PUBLIC_URL}/images/${imageMapping[product.name] || 'default-image.png'}`;

        return (
          <div 
            className="product-card" 
            key={product.id}
            onClick={() => handleClick(product.id)} // Add click handler
          >
            <img src={imageUrl} alt={product.name} />
            <h3>{product.name}</h3>
          </div>
        );
      })}
    </div>
  );
}

export default ProductCard;
