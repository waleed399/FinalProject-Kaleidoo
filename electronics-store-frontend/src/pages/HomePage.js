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
  const defaultImageUrl = '/images/default_no_img.jpg'; // Default image URL

  useEffect(() => {
    async function fetchProducts() {
      try {
        const response = await axios.get('http://localhost:5555/api/products', {
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
    setUserId(userId);
    setAccessToken(accessToken);
    localStorage.setItem('loggedInUser', username);
    localStorage.setItem('userId', userId);
    localStorage.setItem('accessToken', accessToken);
    setIsAuthPopupOpen(false);
    fetchRecommendations(userId);
  };

  const handleLogout = () => {
    setLoggedInUser(null);
    setUserId(null);
    setAccessToken(null);
    setRecommendedProducts([]);
    localStorage.removeItem('loggedInUser');
    localStorage.removeItem('userId');
    localStorage.removeItem('accessToken');
  };

  const handleProductClick = (productId) => {
    console.log(`Product clicked: ${productId}`);
    if (userId) {
      const interactionType = "click";
      const score = 1;

      axios.post('http://localhost:5555/update-interactions', {
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
    if (userId) {
        const interactionType = "search";
        const score = 3;

        axios.post('http://localhost:5555/update-interactions', {
            user_id: userId,
            search_query: searchQuery,
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


  const fetchRecommendations = async (userId) => {
    try {
      const response = await axios.get('http://localhost:5555/get-recommendations', {
        params: { user_id: userId }
      });
  
      if (response.data.recommendations && response.data.recommendations.length > 0) {
        const recommendations = response.data.recommendations;
  
        let parsedRecommendations = [];
  
        if (
          Array.isArray(recommendations) &&
          Array.isArray(recommendations[0]) &&
          Array.isArray(recommendations[0][1])
        ) {
          const imageUrls = recommendations[0][0] || [];
          const details = recommendations[0][1] || [];
  
          parsedRecommendations = details.map(([price, name], index) => ({
            _id: `rec-${index}`,
            price: price,
            name: name,
            image_url: imageUrls[index] || defaultImageUrl
          }));
  
        } else if (
          Array.isArray(recommendations) &&
          recommendations.every(item => typeof item === 'object' && item !== null && 'item_id_numeric' in item && 'name' in item)
        ) {
          parsedRecommendations = recommendations.map((item, index) => ({
            _id: `rec-${index}`,
            item_id_numeric: item.item_id_numeric || 'N/A',
            name: item.name || 'Unnamed Product',
            price: item.price || 'N/A',
            image_url: item.image_url || defaultImageUrl
          }));

        } else {
          console.error('Unexpected format for recommendations data:', recommendations);
          setRecommendedProducts([]);
          return;
        }
  
        setRecommendedProducts(parsedRecommendations);
      } else {
        console.log('No recommendations found');
        setRecommendedProducts([]);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setRecommendedProducts([]);
    }
  };
  

  useEffect(() => {
    if (userId) {
      fetchRecommendations(userId);
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
          <h2>{"Recommended For You"}</h2>
          <div className="recommended-products-list">
            {recommendedProducts.map(product => (
              <div key={product._id} className="recommended-product-card">
                <img src={product.image_url} alt={product.name} />
                <h3>{product.name}</h3>
                {product.price !== 'N/A' && <p>${product.price}</p>}
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
