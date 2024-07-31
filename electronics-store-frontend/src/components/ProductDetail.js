import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios'; // Import axios for API requests
import '../styling/ProductDetail.css';
import imageMapping from '../../src/imageMapping';
import NotificationPopup from './NotificationPopup';

// Function to generate a random price between min and max
const generateRandomPrice = (min = 10, max = 100) => {
  return (Math.random() * (max - min) + min).toFixed(2); // Generate a price and format it to 2 decimal places
};

function ProductDetail({ product }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { loggedInUser, userId } = location.state || {};

  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');
  const [price] = useState(product.price || generateRandomPrice());

  const imageUrl = `${process.env.PUBLIC_URL}/images/${imageMapping[product.name.replace(/\//g, ':')] || 'placeholder.jpg'}`;

  const handlePurchaseClick = () => {
    const userIdFromLocalStorage = localStorage.getItem('userId'); // Retrieve user ID from local storage
    if (loggedInUser && userIdFromLocalStorage) {
      axios.post('http://127.0.0.1:5555/update-interactions', {
        user_id: userIdFromLocalStorage, // Use user ID from local storage
        product_id: product.id,
        interaction_type: 'purchase',
        score: 5
      })
      .then(response => {
        if (response.data.message === 'Interactions updated successfully') {
          setPopupMessage('Product purchased successfully!');
        } else {
          setPopupMessage('Failed to update interactions.');
        }
        setShowPopup(true);

        setTimeout(() => {
          navigate('/'); 
        }, 3000);
      })
      .catch(error => {
        setPopupMessage('Error occurred while updating interactions.');
        setShowPopup(true);
        console.error('Error:', error);
      });
    } else {
      setPopupMessage('You need to be logged in to make a purchase.');
      setShowPopup(true);
    }
  };

  return (
    <div className="product-detail">
      <h1>{product.name}</h1>
      <img src={imageUrl} alt={product.name} />
      <p>Price: ${price}</p>
      <button onClick={handlePurchaseClick}>Purchase</button>

      {showPopup && (
        <NotificationPopup
          message={popupMessage}
          onClose={() => setShowPopup(false)}
        />
      )}
    </div>
  );
}

export default ProductDetail;
