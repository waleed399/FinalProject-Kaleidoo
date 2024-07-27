import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import ProductDetail from '../components/ProductDetail';

function ProductPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);

  useEffect(() => {
    async function fetchProduct() {
      const response = await axios.get(`http://localhost:5555/api/products/${id}`);
      setProduct(response.data);
    }
    fetchProduct();
  }, [id]);

  return (
    <div>
      <button onClick={() => navigate('/')}>Back to Products</button>
      {product ? <ProductDetail product={product} /> : <p>Loading...</p>}
    </div>
  );
}

export default ProductPage;
