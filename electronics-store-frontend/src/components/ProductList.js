import React from 'react';
import ProductItem from './ProductItem';
import '../styling/ProductList.css';

function ProductList({ products }) {
  if (!products.length) {
    return <p>No products found</p>;
  }

  return (
    <div className="product-list">
      {products.map(product => (
        <ProductItem key={product.id} product={product} />
      ))}
    </div>
  );
}

export default ProductList;
