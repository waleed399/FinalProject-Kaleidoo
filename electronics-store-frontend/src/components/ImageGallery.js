import React from 'react';
import ProductCard from './ProductCard';
import './ImageGallery.css';

const images = [
    '4k video camera.jpg',
    '8GB Clip Jam MP3 Player (Black).jpg',
    '10TB G-DRIVE with Thunderbolt.jpg',
    '12 MacBook (Mid 2017, Gold).jpg',
    'AF-S NIKKOR 85mm f:1.8G Lens.jpg',
    'AOC - 18.5 LED Monitor - Black.jpg',
    'Apple iPod Touch 128GB Blue.jpg',
    'AS-5i Pro Sport Earphones (Blue).jpg',
    'Audio Video Shelf.jpg',
    'CD-C600 5-Disc CD Changer.jpg',
    'Cobra - Radar and Laser Detector.jpg',
    'CRX-322 CD Receiver.jpg',
    'Crystal 460X RGB Mid-Tower Case.jpg',
    'E100 1080p Dash Camera.jpg',
    'Expert Mouse Wireless Trackball.jpg',
    'Gear 360 Spherical VR Camera.jpg',
    'GoSafe S30 1080p Dash Cam.jpg',
    'GTK-XB90 Bluetooth Speaker.jpg',
    'HDR-AS200V Full HD Action Cam.jpg',
    'House of Marley.jpg',
    'House of Marley449.jpg',
    'i.am+ Buttons.jpg',
    'Klipsch AW-4i In-Ear Headphones.jpg',
    'Klipsch X20i In-Ear Headphones.jpg',
    'Lenovo Yoga Mouse.jpg',
    'Leviathan Elite Gaming Soundbar.jpg',
    'Lowepro Dashpoint AVC 1, Blue.jpg',
    'Lumix G 25mm f:1.7 ASPH. Lens.jpg',
    'Mini Solar Cell Phone Charger 772.jpg',
    'Mini Solar Cell Phone Charger.jpg',
    'MM8077 7-Channel Power Amplifier.jpg',
    'MX Anywhere 2S Wireless Mouse.jpg',
    'One System Cabinet.jpg',
    'PP999 Phono Preamplifier.jpg',
    'PS200 A:V Component Shelf.jpg',
    'PYLE - Amplifier - Black.jpg',
    'R6i In-Ear Headphones (Black).jpg',
    'RollBarMount.jpg',
    'Samsung J3 - Verizon Prepaid.jpg',
    'SF Slim Lens Pouch 75 AW.jpg',
    'SL-15 Floorstanding Speaker.jpg',
    'slingboxM2.jpg',
    'SRS-ZR7 Wireless Speaker.jpg',
    'TiVo Mini Receiver.jpg',
    'VIRB 360 Action Camera.jpg',
    'VS278Q-P 27 16-9 LCD Monitor.jpg',
    'Wacom CS610PK Bamboo Sketch.jpg',
    'XPS 8920 Tower Desktop Computer.jpg',
    'Flipside 300 Backpack (Black).jpg',
    'SanDisk Extreme Pro 32 GB SDHC.jpg'
  ];
  
  function ImageGallery() {
    return (
      <div className="image-gallery">
        {images.map((image, index) => (
          <ProductCard
            key={index}
            image={image}
            name={image.replace(/(\.[\w\d_-]+)$/i, '').replace(/[-_]/g, ' ')}
          />
        ))}
      </div>
    );
  }
  
  export default ImageGallery;
