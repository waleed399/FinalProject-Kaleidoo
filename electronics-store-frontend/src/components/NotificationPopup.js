import React from 'react';
import '../styling/NotificationPopup.css'; // Add styling for the popup

const NotificationPopup = ({ message, onClose }) => {
  return (
    <div className="notification-popup">
      <div className="popup-content">
        <p>{message}</p>
        <button onClick={onClose}>OK</button>
      </div>
    </div>
  );
}

export default NotificationPopup;
