import React, { useState, useContext, useEffect } from 'react';
import '../styles/index.css';
import Button from 'react-bootstrap/Button';
import ToggleButton from 'react-bootstrap/ToggleButton';
import Form from 'react-bootstrap/Form';
import { DataContext } from '../components/DataContext';

const ShowImage = (props) => {
  if (!(props && props.data && props.data.images )) return ( <>Loading</>)
  const imagesData = props.data
  return (
    <div>
      <div className="">
        {props.showMasks ? (
          <img key="img-mask" src={imagesData.images_with_masks[props.currentIndex]} alt="Mask overlay" className="image"/>
        ) : (
          <img key="img-nomask" src={imagesData.images[props.currentIndex]} alt="Image" className="image"/>
        )}
      </div>
    </div>
  )
}

export default function Images() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [totalImages, setTotalImages] = useState(0);
  const [showMasks, setShowMasks] = useState(false);
  const [classifierResults, setClassifierResults] = useState([]);
  const [selectedImages, setSelectedImages] = useState(new Set());
  const [isResegmenting, setIsResegmenting] = useState(false);
  const { dataState, setDataState } = useContext(DataContext);

  const getPredictions = (state) => (
    state?.classifier_results ??
    state?.info?.classifier_results ??
    state?.predictions ??
    state?.info?.predictions ??
    null
  );

  // Normalize classifier predictions to a Set of indices within [0, numImages)
  const buildPredictedTumorSet = (numImages, predictions) => {
    const tumorSet = new Set();
    if (!predictions || numImages <= 0) return tumorSet;

    if (Array.isArray(predictions)) {
      const arr = predictions;
      const first = arr[0];
      const looksLikeBooleanArray = typeof first === 'boolean' || arr.every(v => typeof v === 'boolean');
      const looksLike01Array = arr.every(v => v === 0 || v === 1 || v === true || v === false);

      // Case A: per-slice boolean/0-1 array (possibly longer than numImages) → map by position and trim
      if (looksLikeBooleanArray || looksLike01Array) {
        const L = Math.min(numImages, arr.length);
        for (let i = 0; i < L; i += 1) {
          const v = arr[i];
          const vv = (typeof v === 'string') ? v.toLowerCase() : v;
          const isPositive = (vv === true || vv === 1 || vv === '1' || vv === 'true' || vv === 'yes');
          if (isPositive) tumorSet.add(i);
        }
        return tumorSet;
      }

      // Case B: list of indices predicted positive
      for (const idx of arr) {
        const n = Number(idx);
        if (!Number.isNaN(n) && n >= 0 && n < numImages) tumorSet.add(n);
      }
      return tumorSet;
    }

    return tumorSet;
  };

  useEffect(() => {
    const count = (dataState && dataState.images) ? dataState.images.length : 0;
    setTotalImages(count);
    setCurrentIndex(0);

    if (dataState?.images && dataState.images.length > 0) {
      const predictions = getPredictions(dataState);
      const tumorSet = buildPredictedTumorSet(dataState.images.length, predictions);

      const results = dataState.images.map((_, index) => ({
        index,
        name: (dataState?.file_names?.[index]) || `MRIm${String(index + 1).padStart(2, '0')}`,
        hasTumor: tumorSet.has(index)
      }));

      // If we have a boolean array exactly matching images length, select the contiguous window first..last true
      let rangeSelected = tumorSet;
      if (Array.isArray(predictions) && predictions.length === dataState.images.length) {
        const first = predictions.findIndex(Boolean);
        const last = predictions.length - 1 - predictions.slice().reverse().findIndex(Boolean);
        if (first !== -1 && last >= first) {
          const win = new Set();
          for (let i = first; i <= last; i += 1) win.add(i);
          rangeSelected = win;
        }
      }

      setClassifierResults(results.map(r => ({ ...r, hasTumor: rangeSelected.has(r.index) })));
      setSelectedImages(rangeSelected);
    } else {
      setClassifierResults([]);
      setSelectedImages(new Set());
    }
  }, [dataState?.study_id, dataState?.images?.length, dataState?.classifier_results, dataState?.file_names]);

  useEffect(() => {
    if (!dataState?.images || dataState.images.length === 0) return;
    const predictions = getPredictions(dataState);
    const tumorSet = buildPredictedTumorSet(dataState.images.length, predictions);

    let rangeSelected = tumorSet;
    if (Array.isArray(predictions) && predictions.length === dataState.images.length) {
      const first = predictions.findIndex(Boolean);
      const last = predictions.length - 1 - predictions.slice().reverse().findIndex(Boolean);
      if (first !== -1 && last >= first) {
        const win = new Set();
        for (let i = first; i <= last; i += 1) win.add(i);
        rangeSelected = win;
      }
    }
    setSelectedImages(rangeSelected);
    setClassifierResults((prev) => prev.map(r => ({ ...r, hasTumor: rangeSelected.has(r.index) })));
  }, [dataState?.classifier_results, dataState?.info?.classifier_results, dataState?.predictions, dataState?.info?.predictions]);

  useEffect(() => {
    if (dataState?.masks_ready) {
      setShowMasks(true);
    }
  }, [dataState?.masks_ready]);

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
    if (!dataState?.masks_ready) return;
    setShowMasks((showMasks) => !showMasks);
  };

  const handleImageClick = (index) => {
    setCurrentIndex(index);
  };

  const handleCheckboxChange = (index, checked) => {
    const newSelected = new Set(selectedImages);
    if (checked) {
      newSelected.add(index);
    } else {
      newSelected.delete(index);
    }
    setSelectedImages(newSelected);
  };

  const handleResegment = async () => {
    if (selectedImages.size === 0 || !dataState?.study_id) return;
    setIsResegmenting(true);
    const apiBase = process.env.REACT_APP_SERVER_API_URL || 'http://localhost:8000';
    const slices = Array.from(selectedImages).map(i => i + 1); // images are 1-based in filenames
    try {
      // 1) Call backend resegment
      const res = await fetch(`${apiBase}/segment/resegment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ study_id: dataState.study_id, slices })
      });
      if (!res.ok) throw new Error('resegment failed');

      // 2) Cache-bust overlays
      setDataState(prev => {
        if (!prev?.images_with_masks) return prev;
        const v = Date.now();
        const bumped = prev.images_with_masks.map(u => `${u}${u.includes('?') ? '&' : '?'}v=${v}`);
        return { ...prev, images_with_masks: bumped };
      });

      // 3) Refresh results using last_job_id
      if (dataState?.last_job_id) {
        const res2 = await fetch(`${apiBase}/results/${dataState.last_job_id}`);
        if (res2.ok) {
          const json2 = await res2.json();
          setDataState(prev => ({
            ...(prev || {}),
            classifier_results: Array.isArray(json2.classifier_results) ? json2.classifier_results : prev?.classifier_results,
            info: {
              ...(prev?.info || {}),
              total_volume: json2.total_volume_cc,
              pixel_spacing_mm: json2.pixel_spacing_mm,
              slice_thickness_mm: json2.slice_thickness_mm,
              slice_areas_cc: json2.slice_areas_cc,
            },
          }));
        }
      }
    } catch (e) {
      // swallow
    } finally {
      setIsResegmenting(false);
    }
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

  return (
    <div className="defaultMainPanel">
      <h2 className="panelTitle">Images</h2>
      
      <div className="imagesMainContainer">
        <div className="imagesLeftPanel">
          <div className="imageViewerContainer">
            <div className="toggleContainer">
              <ToggleButton
                className="toggleButton"
                id="toggle-check"
                type="checkbox"
                variant="outline-success"
                value="1"
                checked={showMasks}
                onChange={toggleMasks}
                disabled={!dataState?.masks_ready}>
                Show masks
              </ToggleButton>
            </div>

            <div className="imageContainer">
              {(dataState) && <ShowImage data={dataState} showMasks={showMasks} currentIndex={currentIndex} /> }
            </div>

            <div className="imageBarContainer">
              <Button className="leftButton"
                variant="primary"
                onClick={handlePrevious}
                disabled={currentIndex === 0}>
                Left
              </Button>{' '}

              <h5>Slice #{currentIndex + 1}</h5>

              <Button className="rightButton"
                variant="primary"
                onClick={handleNext}
                disabled={currentIndex === totalImages - 1}>
                Right
              </Button>{' '}
            </div>
          </div>
        </div>

        <div className="classifierPanel">
          <div className="classifierTitle">Classifier Results</div>
          
          <div className="imageList">
            {classifierResults.map((result) => (
              <div 
                key={result.index}
                className={`imageListItem ${result.index === currentIndex ? 'current' : ''}`}
                onClick={() => handleImageClick(result.index)}
              >
                <Form.Check
                  type="checkbox"
                  className="imageCheckbox"
                  checked={selectedImages.has(result.index)}
                  onChange={(e) => handleCheckboxChange(result.index, e.target.checked)}
                  onClick={(e) => e.stopPropagation()}
                />
                <span className="imageName">{result.name}</span>
              </div>
            ))}
          </div>

          <Button 
            className="resegmentButton"
            variant="warning"
            onClick={handleResegment}
            disabled={selectedImages.size === 0 || isResegmenting}
          >
            {isResegmenting ? 'Resegmenting…' : `Resegment Selected (${selectedImages.size})`}
          </Button>
        </div>
      </div>
    </div>
  );
}


