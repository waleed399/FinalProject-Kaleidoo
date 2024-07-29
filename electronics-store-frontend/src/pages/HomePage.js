import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import MenuBar from '../components/MenuBar';
import Pagination from '../components/Pagination';
import ProductList from '../components/ProductList';
import AuthPopup from '../components/AuthPopup';
import imageMapping from '../imageMapping';
import '../styling/HomePage.css';

function HomePage() {
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isAuthPopupOpen, setIsAuthPopupOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(localStorage.getItem('loggedInUser'));

  const productsPerPage = 12;

  useEffect(() => {
    async function fetchProducts() {
      try {
        const response = await axios.get('http://127.0.0.1:5555/api/products', {
          params: { page: currentPage, limit: productsPerPage }
        });

        if (response.data.products.length > 0) {
          const updatedProducts = response.data.products.map(product => {
            const imageFilename = imageMapping[product.name.toLowerCase()] || 'placeholder.jpg';
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

  const handleReset = () => {
    setSearchTerm('');
    setCurrentPage(1);
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleLoginSuccess = (username) => {
    setLoggedInUser(username);
    localStorage.setItem('loggedInUser', username);
    setIsAuthPopupOpen(false);
  };

  const handleLogout = () => {
    setLoggedInUser(null);
    localStorage.removeItem('loggedInUser');
  };

  return (
    <div>
      <Header />
      <MenuBar 
        onSearch={setSearchTerm} 
        onReset={handleReset} 
        loggedInUser={loggedInUser} 
        onAuthClick={() => setIsAuthPopupOpen(true)} 
        onLogout={handleLogout} 
      />
      <ProductList products={filteredProducts} loggedInUser={loggedInUser}/>
      <Pagination 
        currentPage={currentPage} 
        totalPages={totalPages} 
        onPageChange={setCurrentPage} 
      />
      {isAuthPopupOpen && <AuthPopup onClose={() => setIsAuthPopupOpen(false)} onLoginSuccess={handleLoginSuccess} />}
    </div>
  );
}

export default HomePage;
