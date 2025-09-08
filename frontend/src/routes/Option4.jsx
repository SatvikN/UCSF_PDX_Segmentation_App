import React, { useContext } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { DataContext } from '../components/DataContext';

export default function Saving() {
  const { dataState, setDataState } = useContext(DataContext);
  const studyId = dataState?.study_id;
  const apiBase = process.env.REACT_APP_SERVER_API_URL || 'http://localhost:8000';
  const masksReady = !!dataState?.masks_ready;
  const [prefix, setPrefix] = React.useState('');
  const defaultPrefix = React.useMemo(() => {
    const date = dataState?.info?.study_date || '';
    const pid = dataState?.info?.patient_id || '';
    const base = [date, pid].filter(Boolean).join('_');
    return base;
  }, [dataState?.info?.study_date, dataState?.info?.patient_id]);
  // Keep prefix empty by default; show defaultPrefix visually as placeholder.
  // Downloads use effectivePrefix = prefix || defaultPrefix.
  React.useEffect(() => {
    // no-op: avoid auto-overwriting user input
  }, [defaultPrefix, studyId]);
  const effectivePrefix = prefix || defaultPrefix;

  // Ensure metadata is available for default prefix even if Info panel wasn't visited
  React.useEffect(() => {
    const fetchMeta = async () => {
      if (!studyId) return;
      try {
        const res = await fetch(`${apiBase}/studies/${studyId}/info`);
        if (res.ok) {
          const meta = await res.json();
          setDataState?.((prev) => ({ ...(prev || {}), info: { ...(prev?.info || {}), ...meta } }));
        }
      } catch (_e) {
        // ignore
      }
    };
    if (studyId && !dataState?.info) {
      fetchMeta();
    }
  }, [studyId, apiBase, dataState?.info, setDataState]);

  const download = (url, filename) => {
    const a = document.createElement('a');
    a.href = url;
    if (filename) a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const handleDownloadOverlays = () => {
    if (!studyId) return;
    const q = effectivePrefix ? `&prefix=${encodeURIComponent(effectivePrefix)}` : '';
    const name = `${effectivePrefix ? `${effectivePrefix}_` : ''}overlays.zip`;
    download(`${apiBase}/export/${studyId}/images.zip?kind=overlays${q}`, name);
  };

  const handleDownloadMasks = () => {
    if (!studyId) return;
    const q = effectivePrefix ? `&prefix=${encodeURIComponent(effectivePrefix)}` : '';
    const name = `${effectivePrefix ? `${effectivePrefix}_` : ''}masks.zip`;
    download(`${apiBase}/export/${studyId}/images.zip?kind=masks${q}`, name);
  };

  const handleDownloadPNGs = () => {
    if (!studyId) return;
    const q = effectivePrefix ? `&prefix=${encodeURIComponent(effectivePrefix)}` : '';
    const name = `${effectivePrefix ? `${effectivePrefix}_` : ''}images.zip`;
    download(`${apiBase}/export/${studyId}/images.zip?kind=pngs${q}`, name);
  };

  const handleDownloadImagesNPZ = () => {
    if (!studyId) return;
    const q = effectivePrefix ? `?prefix=${encodeURIComponent(effectivePrefix)}` : '';
    const name = `${effectivePrefix ? `${effectivePrefix}_` : ''}images.npz`;
    download(`${apiBase}/export/${studyId}/images.npz${q}`, name);
  };

  const handleDownloadMasksNPZ = () => {
    if (!studyId) return;
    const params = new URLSearchParams();
    params.append('format', 'npz');
    if (effectivePrefix) params.append('prefix', effectivePrefix);
    const name = `${effectivePrefix ? `${effectivePrefix}_` : ''}masks.npz`;
    download(`${apiBase}/export/${studyId}/masks?${params.toString()}`, name);
  };

  const handleDownloadMasksMAT = () => {
    if (!studyId) return;
    const params = new URLSearchParams();
    params.append('format', 'mat');
    if (effectivePrefix) params.append('prefix', effectivePrefix);
    const name = `${effectivePrefix ? `${effectivePrefix}_` : ''}masks.mat`;
    download(`${apiBase}/export/${studyId}/masks?${params.toString()}`, name);
  };

  const handleDownloadExcel = () => {
    if (!studyId) return;
    const q = effectivePrefix ? `?prefix=${encodeURIComponent(effectivePrefix)}` : '';
    const name = `${effectivePrefix ? `${effectivePrefix}_` : ''}volumes.xlsx`;
    download(`${apiBase}/export/${studyId}/volumes.xlsx${q}`, name);
  };
  return (
    <div className="defaultMainPanel">
      <h2 className="panelTitle">Saving</h2>
      <div className="modelTextBox">
        <div className="savingFields">
          <div className="modelDropdown">
            <div className="savingRow" style={{ alignItems: 'center', gap: '0.5rem' }}>
              <Form.Label style={{ margin: 0, whiteSpace: 'nowrap', fontSize: '1.25rem', fontWeight: 700 }}>Set prefix for saved file names:</Form.Label>
              <Form.Control style={{ width: 'clamp(320px, 70%, 720px)' }} type="text" placeholder={defaultPrefix} value={prefix} onChange={(e) => setPrefix(e.target.value)} />
            </div>
          </div>
          <div className="savingSectionTitle">Images</div>
          <div className="modelDropdown">
            <div className="savingRow">
              <Button className="wideButton" variant="outline-primary" onClick={handleDownloadPNGs} disabled={!studyId}>Download tumor images only<br/>(png)</Button>
              <Button className="wideButton" variant="outline-primary" onClick={handleDownloadImagesNPZ} disabled={!studyId}>Download tumor images only<br/>(numpy array)</Button>
            </div>
          </div>
          <div className="modelDropdown">
            <div className="savingRow">
              <Button className="wideButton" variant="outline-secondary" onClick={handleDownloadMasks} disabled={!studyId || !masksReady}>Download masks only<br/>(png)</Button>
              <Button className="wideButton" variant="outline-secondary" onClick={handleDownloadMasksNPZ} disabled={!studyId || !masksReady}>Download masks only<br/>(numpy array)</Button>
              <Button className="wideButton" variant="outline-info" onClick={handleDownloadMasksMAT} disabled={!studyId || !masksReady}>Download masks only<br/>(MATLAB .mat)</Button>
            </div>
          </div>
          <div className="modelDropdown">
            <div className="savingRow">
              <Button className="wideButton" variant="outline-success" onClick={handleDownloadOverlays} disabled={!studyId || !masksReady}>Download image + mask overlays<br/>(png)</Button>
            </div>
          </div>
          <div className="savingSectionTitle">Save volume calculations (Excel)</div>
          <div className="modelDropdown">
            <div className="savingRow">
              <Button className="wideButton" variant="outline-primary" onClick={handleDownloadExcel} disabled={!studyId || !masksReady}>Download volumes.xlsx</Button>
            </div>
            <div style={{ fontSize:  '0.9rem', marginTop: '0.5rem' }}>
              Excel includes raw pixel counts per slice and formulas using pixel spacing and slice thickness, so you can adjust parameters later.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


