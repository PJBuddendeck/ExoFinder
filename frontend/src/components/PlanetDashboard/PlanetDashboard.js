import React, { useEffect } from 'react';
import './PlanetDashboard.css';

const PlanetModal = ({ planet, onClose }) => {
    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => {
        document.body.style.overflow = 'unset';
        };
    }, []);
    
  // Helper for wavelength display
  const hasSpec = planet.minwavelng && planet.maxwavelng;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>&times;</button>
        
        <header className="modal-header">
          <h2>{planet.pl_name}</h2>
          <p className="subtitle">System: {planet.hostname} | Discovered: {planet.disc_year}</p>
        </header>

        <section className="modal-body">
          <div className="info-group">
            <h4>Atmospheric Spectroscopy</h4>
            {hasSpec ? (
              <div className="spec-data">
                <p><strong>Range:</strong> {planet.minwavelng} - {planet.maxwavelng} microns</p>
                <p><strong>Instrument:</strong> {planet.spec_facility || "Multiple/Ground"}</p>
                <p><strong>Type:</strong> {planet.spec_type || "N/A"}</p>
              </div>
            ) : (
              <p className="no-data">No spectroscopic data available for this target.</p>
            )}
          </div>

          <div className="info-group">
            <h4>System Context</h4>
            <p><strong>Orbital Period:</strong> {planet.pl_orbper?.toFixed(2)} days</p>
            <p><strong>Star Temperature:</strong> {planet.st_teff} K</p>
            <p><strong>Star Radius:</strong> {planet.st_rad} R☉</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default PlanetModal;