import React, { useEffect } from 'react';
import './PlanetDashboard.css';

const PlanetModal = ({ planet, onClose }) => {
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);


const formatUnknown = (value) => {
    return value === null || value === undefined ? "Unknown" : value;
};

const formatDecimal = (value, dec) => {
    value = formatUnknown(value);
    if (value==='Unknown') return "Unknown";
    return Number(value).toFixed(dec);
};

const hasSpec = planet.minwavelng && planet.maxwavelng;

return (
  <div className="modal-overlay" onClick={onClose}>
    {/* 1. Modal Content MUST have display: flex and a max-height */}
    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
      
      <button className="close-btn" onClick={onClose} aria-label="Close modal">
        &times;
      </button>
      
      <header className="modal-header">
        <h2>{planet.pl_name}</h2>
        <p className="subtitle">System: {planet.hostname} | Discovered: {planet.disc_year}</p>
      </header>

      {/* 2. This DIV is the magic. It MUST be the only scrollable area */}
      <div className="modal-scroll-area">
        <div className="info-group">
          <h4>Physical Profile</h4>
          <div className="system-grid">
              <p><strong>Mass:</strong> {formatDecimal(planet.pl_bmasse, 2)} M⊕</p>
              <p><strong>Radius:</strong> {formatDecimal(planet.pl_rade, 2)} R⊕</p>
              <p><strong>ESI:</strong> {formatDecimal(planet.pl_esi, 3)}</p>
          </div>
        </div>

        <div className="info-group">
          <h4>System Context</h4>
          <p><strong>Orbital Period:</strong> {formatDecimal(planet.pl_orbper, 2)} days</p>
          <p><strong>Star Temp:</strong> {formatDecimal(planet.st_teff, 2)} K</p>
          <p><strong>Distance:</strong> {formatDecimal(planet.sy_dist, 2)} pc</p>
        </div>

        <div className="info-group">
          <h4>Atmospheric Spectroscopy</h4>
          {hasSpec ? (
            <div className="spec-data">
              <p><strong>Range:</strong> {planet.minwavelng} - {planet.maxwavelng} microns</p>
              <p><strong>Instrument:</strong> {planet.spec_facility || "NASA TAP"}</p>
              <p><strong>Type:</strong> {planet.spec_type || "N/A"}</p>
            </div>
          ) : (
            <p className="no-data">No spectroscopic data available.</p>
          )}
        </div>
        
        {/* Spacer to ensure scrolling is visible during testing */}
      </div>
    </div>
  </div>
);
};

export default PlanetModal;