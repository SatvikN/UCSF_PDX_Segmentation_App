import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/index.css';
import logo from '../assets/logo.png';
import Form from 'react-bootstrap/Form';
import { DataContext } from '../components/DataContext';

export default function Header() {
  const [files, setFiles] = useState([]);
  const [isSegmenting, setIsSegmenting] = useState(false);
  const { dataState, setDataState } = useContext(DataContext);
  const navigate = useNavigate();

  const studyId = dataState?.study_id || '';

  const onFileChange = (e) => {
    const picked = Array.from(e.target.files || []);
    const dcmOnly = picked.filter((f) => f.name.toLowerCase().endsWith('.dcm'));
    setFiles(dcmOnly);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!files.length) return;
    const form = new FormData();
    files.forEach((f) => form.append('files', f));
    const apiBase = process.env.REACT_APP_SERVER_API_URL || 'http://localhost:8000';
    const res = await fetch(`${apiBase}/files/upload`, { method: 'POST', body: form });
    const json = await res.json();
    const sid = json.study_id;
    const total = (json.files || []).length;
    const images = Array.from({ length: total }, (_, i) => `${apiBase}/images/${sid}/${i + 1}.png`);
    const images_with_masks = Array.from({ length: total }, (_, i) => `${apiBase}/images/${sid}/${i + 1}/overlay.png`);
    const file_names = json.files || [];
    setDataState({ study_id: sid, images, images_with_masks, file_names, info: {} });
    navigate('/images');
  };

  const handleSegment = async () => {
    if (!studyId || isSegmenting) return;
    setIsSegmenting(true);
    const apiBase = process.env.REACT_APP_SERVER_API_URL || 'http://localhost:8000';
    const start = await fetch(`${apiBase}/segment/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ study_id: studyId })
    });
    const { job_id } = await start.json();
    setDataState((prev) => ({ ...(prev || {}), last_job_id: job_id }));
    const poll = async () => {
      const r = await fetch(`${apiBase}/segment/${job_id}/status`);
      const j = await r.json();
      if (j.status === 'done') {
        setDataState((prev) => {
          if (!prev || !prev.images_with_masks) return prev;
          const v = Date.now();
          const bumped = prev.images_with_masks.map((u) => `${u}${u.includes('?') ? '&' : '?'}v=${v}`);
          return { ...prev, images_with_masks: bumped, masks_ready: true };
        });
        try {
          const apiBase2 = process.env.REACT_APP_SERVER_API_URL || 'http://localhost:8000';
          const res2 = await fetch(`${apiBase2}/results/${job_id}`);
          if (res2.ok) {
            const json2 = await res2.json();
            const derivedClassifier = Array.isArray(json2.classifier_results)
              ? json2.classifier_results
              : (Array.isArray(json2.slice_areas_cc)
                  ? json2.slice_areas_cc.map((area) => Number(area) > 0)
                  : undefined);
            setDataState((prev) => ({
              ...(prev || {}),
              classifier_results: derivedClassifier ?? prev?.classifier_results,
              info: {
                ...(prev?.info || {}),
                total_volume: json2.total_volume_cc,
                pixel_spacing_mm: json2.pixel_spacing_mm,
                slice_thickness_mm: json2.slice_thickness_mm,
                slice_areas_cc: json2.slice_areas_cc,
              },
            }));
          }
        } catch (_) {}
        setIsSegmenting(false);
        return;
      }
      if (j.status === 'error') {
        setIsSegmenting(false);
        return;
      }
      setTimeout(poll, 1000);
    };
    poll();
  };

  return (
    <div className="header">
      <div className="header-left">
        <img src={logo} alt="Logo" className="logo" />
      </div>
      <div className="header-right">
        <div className="header-actions">
          <Form onSubmit={handleSubmit}>
            <div className="path-container">
              <Form.Group controlId="upload-dicom" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div className="path-label">
                  <Form.Label>Upload DICOMs:</Form.Label>
                </div>
                <div className="path-input">
                  <Form.Control type="file" multiple accept=".dcm" onChange={onFileChange} />
                </div>
                <div className='path-button'>
                  <button type="submit" className="btn btn-primary">Upload</button>
                </div>
                <div>
                  <button
                    type="button"
                    className="btn btn-success"
                    onClick={handleSegment}
                    disabled={!studyId || isSegmenting}
                  >
                    {isSegmenting ? 'Segmenting…' : 'Run Segmentation'}
                  </button>
                </div>
              </Form.Group>
            </div>
          </Form>
        </div>
      </div>
    </div>
  );
}


