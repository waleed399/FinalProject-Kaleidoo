import React from 'react';
import ProductItem from './ProductItem';
import '../styling/ProductList.css';

const ProductList = ({ products, loggedInUser }) => {
  // Filter products to ensure unique names
  const uniqueProducts = Array.from(
    new Map(products.map(product => [product.name, product])).values()
  );

  return (
    <div className="product-list">
      {uniqueProducts.map(product => (
        <ProductItem key={product.id} product={product} loggedInUser={loggedInUser}/>
      ))}
    </div>
  );
}

export default ProductList;
