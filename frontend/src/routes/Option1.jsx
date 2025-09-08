import React, { useState } from 'react';
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Form from 'react-bootstrap/Form';

export default function Models() {
  const [selectedAnatomy, setSelectedAnatomy] = useState('Select Anatomy');
  const [selectedArch, setSelectedArch] = useState('Select Architecture');
  const [selectedWeights, setSelectedWeights] = useState('Select Weights');
  const [manualSelect, setManualSelect] = useState(true);

  const handleAnatomy = (eventKey) => setSelectedAnatomy(eventKey);
  const handleArch = (eventKey) => setSelectedArch(eventKey);
  const handleWeights = (eventKey) => setSelectedWeights(eventKey);

  return (
    <div className="defaultMainPanel modelsPanel">
      <h2 className="panelTitle">Model Selection</h2>
      <div className="modelTextBox">
        <div className="modelDropdown">
          <div className="field-label">
            <Form.Check
              type="checkbox"
              id="manual-select-toggle"
              className="largeCheckbox"
              checked={manualSelect}
              onChange={(e) => setManualSelect(e.currentTarget.checked)}
              label={<><span>Use default weights and architecture to perform segmentation</span><br/>(Otherwise manually select the weights and architecture)<br/>Default weights are for a DR2UNET model trained on kidney, liver, and tibia anatomies</>}
            />
          </div>
        </div>
        <div className="modelFields">
          <div className="modelDropdown">
            <div className="field-label">What is the anatomy of the tumors you wish to segment? (Select general for model trained on all anatomies)</div>
            <DropdownButton className="fixed-dd" id="dropdown-anatomy" title={selectedAnatomy} onSelect={handleAnatomy} variant="outline-primary" disabled={manualSelect}>
              <Dropdown.Item eventKey="Kidney">Kidney</Dropdown.Item>
              <Dropdown.Item eventKey="Liver">Liver</Dropdown.Item>
              <Dropdown.Item eventKey="Tibia">Tibia</Dropdown.Item>
            </DropdownButton>
          </div>
          <div className="modelDropdown">
            <div className="field-label">Model Architecture</div>
            <DropdownButton className="fixed-dd" id="dropdown-arch" title={selectedArch} onSelect={handleArch} variant="outline-primary" disabled={manualSelect}>
              <Dropdown.Item eventKey="R2UDenseNet">R2UDenseNet</Dropdown.Item>
              <Dropdown.Item eventKey="UNet">UNet</Dropdown.Item>
              <Dropdown.Item eventKey="ResUNet">ResUNet</Dropdown.Item>
            </DropdownButton>
          </div>
          <div className="modelDropdown">
            <div className="field-label">Weights</div>
            <DropdownButton className="fixed-dd" id="dropdown-weights" title={selectedWeights} onSelect={handleWeights} variant="outline-primary" disabled={manualSelect}>
              <Dropdown.Item eventKey="Default Weights">Default Weights</Dropdown.Item>
              <Dropdown.Item eventKey="Kidney_v1.h5">Kidney_v1.h5</Dropdown.Item>
              <Dropdown.Item eventKey="Liver_v2.h5">Liver_v2.h5</Dropdown.Item>
            </DropdownButton>
          </div>
      </div>
      </div>
    </div>
  );
}


