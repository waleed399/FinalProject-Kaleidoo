import React, { useState } from 'react'; // Removed useEffect import
import { useLocation, useNavigate } from 'react-router-dom';
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
  const { loggedInUser } = location.state || {}; // Access loggedInUser from state

  // State for managing popup visibility and message
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');

  // State for storing the price, initialized only once
  const [price] = useState(product.price || generateRandomPrice());

  // Use the product name to get the correct image URL from the mapping
  const imageUrl = `${process.env.PUBLIC_URL}/images/${imageMapping[product.name]}`;

  // Button click handler
  const handlePurchaseClick = () => {
    if (loggedInUser) {
      // Proceed with purchase
      setPopupMessage('Product purchased successfully!');
      setShowPopup(true);

      // Navigate back to the main page after a delay
      setTimeout(() => {
        navigate('/'); // Navigate back to the main page after a delay
      }, 3000); // Adjust the delay as needed
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

      {/* Conditionally render the NotificationPopup */}
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
