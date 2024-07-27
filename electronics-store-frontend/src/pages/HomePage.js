import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import MenuBar from '../components/MenuBar'; // Use MenuBar for search functionality
import Pagination from '../components/Pagination';
import ProductList from '../components/ProductList';
import imageMapping from '../imageMapping'; // Import the image mapping
import '../styling/HomePage.css';

function HomePage() {
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const productsPerPage = 10;  // Set to 10 products per page

  useEffect(() => {
    async function fetchProducts() {
      try {
        const response = await axios.get('http://127.0.0.1:5555/api/products', {
          params: { page: currentPage, limit: productsPerPage }
        });
        console.log("Fetched products:", response.data); // Log the response data

        if (response.data.products.length > 0) {
          // Map products to include image filename
          const updatedProducts = response.data.products.map(product => {
            const imageFilename = imageMapping[product.name.toLowerCase()] || 'placeholder.jpg'; // Fallback to placeholder
            return {
              ...product,
              image: imageFilename
            };
          });

          setProducts(updatedProducts);
          setTotalPages(response.data.totalPages);
        } else {
          setProducts([]);
        }
      } catch (error) {
        console.error("There was an error fetching the products!", error);
      }
    }
    fetchProducts();
  }, [currentPage]);

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  console.log("Filtered products:", filteredProducts);

  return (
    <div>
      <Header />
      <MenuBar onSearch={setSearchTerm}/>
      <ProductList products={filteredProducts} />
      <Pagination 
        currentPage={currentPage} 
        totalPages={totalPages} 
        onPageChange={setCurrentPage} 
      />
    </div>
  );
}

export default HomePage;
