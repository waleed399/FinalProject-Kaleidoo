// src/components/ContactPage.js
import React from 'react';
import { Link } from 'react-router-dom';
import '../styling/ContactPage.css';

function ContactPage() {

  return (
    <div className="contact-page">
      <h1>Contact Us</h1>
      <p>Welcome to Techtronix! We are committed to providing you with the best electronic products. If you have any questions or need support, please reach out to us.</p>
      <p>Email: <a href="mailto:waleed.ali1797@gmail.com">waleed.ali1797@gmail.com</a></p>
      <Link to="/" className='return-home-button'>Return to Homepage</Link>
    </div>
  );
}

export default ContactPage;
