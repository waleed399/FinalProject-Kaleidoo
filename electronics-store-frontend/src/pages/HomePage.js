import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import MenuBar from '../components/MenuBar';
import Pagination from '../components/Pagination';
import ProductList from '../components/ProductList';
import AuthPopup from '../components/AuthPopup';
import '../styling/HomePage.css';

function HomePage() {
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isAuthPopupOpen, setIsAuthPopupOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(localStorage.getItem('loggedInUser'));
  const [userId, setUserId] = useState(localStorage.getItem('userId'));
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));
  const [recommendedProducts, setRecommendedProducts] = useState([]);

  const productsPerPage = 12;

  useEffect(() => {
    async function fetchProducts() {
      try {
        const response = await axios.get('http://127.0.0.1:5555/api/products', {
          params: { page: currentPage, limit: productsPerPage }
        });

        if (response.data.products.length > 0) {
          setProducts(response.data.products);
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

  const handleLoginSuccess = (username, userId, accessToken) => {
    setLoggedInUser(username);
    setUserId(userId); // Store the user ID
    setAccessToken(accessToken); // Store the access token
    localStorage.setItem('loggedInUser', username);
    localStorage.setItem('userId', userId); // Store user ID in localStorage
    localStorage.setItem('accessToken', accessToken); // Store access token in localStorage
    setIsAuthPopupOpen(false);
  };

  const handleLogout = () => {
    setLoggedInUser(null);
    setUserId(null);
    setAccessToken(null);
    setRecommendedProducts([]); // Clear recommendations on logout
    localStorage.removeItem('loggedInUser');
    localStorage.removeItem('userId');
    localStorage.removeItem('accessToken');
  };

  const handleProductClick = (productId) => {
    console.log(`Product clicked: ${productId}`);
    console.log(`user_id : ${userId}`);
    if (userId) {
      const interactionType = "click";
      const score = 1;

      axios.post('http://127.0.0.1:5555/update-interactions', {
        user_id: userId,
        product_id: productId,
        interaction_type: interactionType,
        score: score
      })
      .then(response => {
        if (response.data.message === 'Interactions updated successfully') {
          console.log('Interactions updated successfully.');
        } else {
          console.error('Failed to update interactions:', response.data.error);
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }
  };

  const handleSearch = (searchQuery) => {
    console.log(`Search performed: ${searchQuery}`);
    console.log(`user_id : ${userId}`);
    if (userId) {
        const interactionType = "search";
        const score = 3;

        axios.post('http://127.0.0.1:5555/update-interactions', {
            user_id: userId,
            search_query: searchQuery,  // Pass the search query if needed
            interaction_type: interactionType,
            score: score
        })
        .then(response => {
            if (response.data.message === 'Interactions updated successfully') {
                console.log('Interactions updated successfully.');
            } else {
                console.error('Failed to update interactions:', response.data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
  };

  const fetchRecommendations = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5555/get-recommendations', {
            params: { user_id: userId }
        });

        if (response.data.recommendations) {
            // Map the data to an array of objects
            const recommendations = response.data.recommendations.map(([product_id, price, name]) => ({
                _id: product_id,
                price: price,
                name: name,
                image_url: 'path/to/default/image.jpg', // Placeholder for image URL
            }));

            setRecommendedProducts(recommendations);
        } else {
            console.log('No recommendations found');
            setRecommendedProducts([]);
        }
    } catch (error) {
        console.error('Error fetching recommendations:', error);
    }
  };

  useEffect(() => {
    if (userId) {
        fetchRecommendations();
    }
  }, [userId]);

  return (
    <div>
        <Header />
        <MenuBar 
            onSearch={(query) => { setSearchTerm(query); handleSearch(query); }} 
            onReset={handleReset} 
            loggedInUser={loggedInUser} 
            onAuthClick={() => setIsAuthPopupOpen(true)} 
            onLogout={handleLogout} 
        />
        <ProductList 
            products={filteredProducts} 
            loggedInUser={loggedInUser}
            onProductClick={handleProductClick}
        />
        {recommendedProducts.length > 0 && (
            <div className="recommended-products">
                <h2>Recommended for You</h2>
                <div className="recommended-products-list">
                    {recommendedProducts.map(product => (
                        <div key={product._id} className="recommended-product-card">
                            <img src={product.image_url} alt={product.name} />
                            <h3>{product.name}</h3>
                            <p>${product.price}</p>
                            <button onClick={() => handleProductClick(product._id)}>View Details</button>
                        </div>
                    ))}
                </div>
            </div>
        )}
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
