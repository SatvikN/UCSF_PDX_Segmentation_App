import React, { useState, useContext, useEffect } from 'react';
import '../styles/index.css';
import Button from 'react-bootstrap/Button';
import ToggleButton from 'react-bootstrap/ToggleButton';
import { DataContext } from '../components/DataContext';
import WelcomePanel from '../components/WelcomePanel';

const ShowImage = (props) => {
  if (!(props && props.data && props.data.images )) return ( <>Loading</>)
  const imagesData = props.data
  return (
    <div>
      <div className="imageContainer">
        {props.showMasks ? (
          <img key="img-mask" src={imagesData.images_with_masks[props.currentIndex]} alt="Base64 mask Example" className="image"/>
        ) : (
          <img key="img-nomask" src={imagesData.images[props.currentIndex]} alt="Base64 Example" className="image"/>
        )}
      </div>
    </div>
  )
}

export default function Home() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [totalImages, setTotalImages] = useState(0);
  const [showMasks, setShowMasks] = useState(false);
  const { dataState } = useContext(DataContext);
  const hasImages = !!(dataState && Array.isArray(dataState.images) && dataState.images.length > 0);

  useEffect(() => {
    const count = (dataState && dataState.images) ? dataState.images.length : 0;
    setTotalImages(count);
    setCurrentIndex(0);
  }, [dataState?.study_id, dataState?.images?.length]);

  const handleNext = () => {
    if (currentIndex < totalImages - 1) {
      setCurrentIndex((prevIndex) => prevIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prevIndex) => prevIndex - 1);
    }
  };

  const toggleMasks = () => {
    setShowMasks((showMasks) => !showMasks);
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowRight') {
        e.preventDefault();
        handleNext();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        handlePrevious();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, totalImages]);

  if (!hasImages) {
    return (
      <div className="main-container">
        <WelcomePanel />
      </div>
    );
  }

  return (
    <div className="main-container">
      <WelcomePanel />
    </div>
  );
}


