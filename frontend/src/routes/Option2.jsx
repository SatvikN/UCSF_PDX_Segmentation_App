import React, { useContext, useEffect, useState } from 'react';
import { DataContext } from '../components/DataContext';

const ShowInfo = ({ data }) => {
  const info = (data && data.info) ? data.info : {};
  const rows = [
    { label: 'Study Date', value: info.study_date },
    { label: 'Patient ID', value: info.patient_id },
    { label: 'Patient Weight', value: info.patient_weight },
    { label: 'Pixel Spacing (mm)', value: info.pixel_spacing_mm ? info.pixel_spacing_mm.join(' × ') : undefined },
    { label: 'Slice Thickness (mm)', value: info.slice_thickness_mm },
    { label: 'Spacing Between Slices (mm)', value: info.spacing_between_slices_mm },
    { label: 'Image Height (px)', value: info.height },
    { label: 'Image Width (px)', value: info.width },
    { label: 'Total Tumor Volume (cc)', value: info.total_volume }
  ];
  const acquisition = [
    { label: 'Echo Time (TE)', value: info.echo_time },
    { label: 'Repetition Time (TR)', value: info.repetition_time },
    { label: 'Sequence Name', value: info.sequence_name },
    { label: 'Sequence Variant', value: info.sequence_variant },
    { label: 'Echo Train Length', value: info.echo_train_length },
  ];
  return (
    <>
      <div className="kvTable">
        {rows.map((r) => (
          <div key={r.label} className="kvRow">
            <div className="kvKey">{r.label}</div>
            <div className="kvVal">{r.value ?? '—'}</div>
          </div>
        ))}
      </div>
      <div className="kvSectionTitle">Additional Information from Metadata:</div>
      <div className="kvTable">
        {acquisition.map((r) => (
          <div key={r.label} className="kvRow">
            <div className="kvKey">{r.label}</div>
            <div className="kvVal">{r.value ?? '—'}</div>
          </div>
        ))}
      </div>
    </>
  );
};

export default function Calculations() {
  const { dataState, setDataState } = useContext(DataContext);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError('');
      try {
        const apiBase = process.env.REACT_APP_SERVER_API_URL || 'http://localhost:8000';
        if (dataState?.study_id) {
          const metaRes = await fetch(`${apiBase}/studies/${dataState.study_id}/info`);
          if (metaRes.ok) {
            const meta = await metaRes.json();
            setDataState((prev) => ({ ...(prev || {}), info: { ...(prev?.info || {}), ...meta } }));
          }
        }
        if (dataState?.last_job_id) {
          const res = await fetch(`${apiBase}/results/${dataState.last_job_id}`);
          if (res.ok) {
            const json = await res.json();
            setDataState((prev) => ({ ...(prev || {}), info: { ...(prev?.info || {}), total_volume: json.total_volume_cc, pixel_spacing_mm: json.pixel_spacing_mm, slice_thickness_mm: json.slice_thickness_mm } }));
          }
        }
      } catch (_e) {
        setError('Failed to fetch results');
      } finally {
        setLoading(false);
      }
    };
    if (dataState?.study_id) run();
  }, [dataState?.study_id, dataState?.last_job_id, setDataState]);
  return (
    <div className="defaultMainPanel">
      <h2 className="panelTitle">Information & Calculations</h2>
      {error ? <div style={{ color: 'crimson' }}>{error}</div> : null}
      <div style={{ marginTop: '1rem' }} className="modelTextBox">
        <ShowInfo data={dataState || {}} />
      </div>
    </div>
  )
}


