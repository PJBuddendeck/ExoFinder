import React, { useEffect } from 'react';
import './PlanetDashboard.css';

const PlanetModal = ({ planet, onClose }) => {
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

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
               <p><strong>Mass:</strong> {planet.pl_bmasse?.toFixed(2)} M⊕</p>
               <p><strong>Radius:</strong> {planet.pl_rade?.toFixed(2)} R⊕</p>
               <p><strong>Gravity:</strong> {planet.pl_gravity?.toFixed(2)} g</p>
               <p><strong>ESI:</strong> {planet.pl_esi?.toFixed(3) || "N/A"}</p>
            </div>
          </div>

          <div className="info-group">
            <h4>System Context</h4>
            <p><strong>Orbital Period:</strong> {planet.pl_orbper?.toFixed(2)} days</p>
            <p><strong>Star Temp:</strong> {planet.st_teff?.toFixed(2)} K</p>
            <p><strong>Distance:</strong> {planet.sy_dist?.toFixed(2)} pc</p>
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
          <div style={{ height: '50px' }}></div>
        </div>
      </div>
    </div>
  );
};

export default PlanetModal;