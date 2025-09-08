import React from 'react';

export default function WelcomePanel() {
  return (
    <div className="welcome-panel">
      <h2 style={{ textAlign: 'center' }}>Welcome to the PDX Segmentation App</h2>
      <p>
        We developed this platform to support researchers by automating the manual segmentation process to compute the tumor volumes of PDX models.
      </p>
      <p>
        For more information about our research methodology, please refer to our manuscript:
        <br />
        <a href="https://doi.org/10.3390/tomography11030021" target="_blank" rel="noopener noreferrer">
          Deep Learning-Based Tumor Segmentation of Murine Magnetic Resonance Images of Prostate Cancer Patient-Derived Xenografts
        </a>
      </p>
      <p>
        To get started:
      </p>
      <ol>
        <li>Use the Upload DICOMs control in the header to select .dcm files</li>
        <li>Click Upload to load images into the app</li>
        <li>Optionally, click Run Segmentation to compute masks and volumes</li>
      </ol>
      <p>
        You can also explore the sections from the left sidebar: Model Selection, Information & Calculations, Images, and Saving.
      </p>
    </div>
  );
}


