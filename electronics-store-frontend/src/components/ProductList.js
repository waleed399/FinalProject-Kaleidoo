import React from 'react';
import ProductItem from './ProductItem';
import '../styling/ProductList.css';

const ProductList = ({ products, loggedInUser, onProductClick, onPurchaseClick }) => {
  // Filter products to ensure unique names
  const uniqueProducts = Array.from(
    new Map(products.map(product => [product.name, product])).values()
  );

  return (
    <div className="product-list">
      {uniqueProducts.map(product => (
        <ProductItem 
          key={product.id} 
          product={product} 
          loggedInUser={loggedInUser}
          onProductClick={onProductClick} // Pass click handler to ProductItem
          onPurchaseClick={onPurchaseClick} // Pass purchase handler to ProductItem
        />
      ))}
    </div>
  );
}

export default ProductList;
