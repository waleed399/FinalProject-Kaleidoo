import React from 'react';
import '../styling/ProductDetail.css';
import imageMapping from '../../src/imageMapping';  // Update the import path

function ProductDetail({ product }) {
  // Use the product name to get the correct image URL from the mapping
  const imageUrl = `${process.env.PUBLIC_URL}/images/${imageMapping[product.name]}`;

  return (
    <div className="product-detail">
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <img src={imageUrl} alt={product.name} />
      <p>Brand: {product.brand}</p>
      <button>Purchase</button>
    </div>
  );
}

export default ProductDetail;
