import React from 'react';
import './ResultGrid.css'

const formatUnknown = (value) => {
    return value === null || value === undefined ? "Unknown" : value;
};

const formatDecimal = (value, dec) => {
    value = formatUnknown(value);
    if (value==='Unknown') return "Unknown";
    return Number(value).toFixed(dec);
};

const ResultGrid = ({ planets, onPlanetClick }) => {
  return (
    <div className="results-grid">
      {planets.map((p, i) => (
        
        <div 
          key={i} 
          className="planet-card" 
          onClick={() => onPlanetClick(p)} // Call the function here
          style={{ cursor: 'pointer' }}
        >
          <div className="card-header">
            <h3>{p.pl_name}</h3>
            <span className="host-star">System: {p.hostname}</span>
          </div>
          
          <div className="card-stats">
            <div className="stat-item">
              <label>Distance</label>
              <span>{formatDecimal(p.sy_dist, 2)} pc</span>
            </div>
            <div className="stat-item">
              <label>Discovered</label>
              <span>{formatUnknown(p.disc_year)}</span>
            </div>
            <div className="stat-item">
              <label>Mass</label>
              <span>{formatDecimal(p.pl_bmasse, 2)} M⊕</span>
            </div>
            <div className="stat-item">
              <label>Radius</label>
              <span>{formatDecimal(p.pl_rade, 2)} R⊕</span>
            </div>
          </div>

          <div className="card-footer">
            {p.pl_eqt && (
            <span className="temp-badge">EQT: {formatDecimal(p.pl_eqt, 0)} K</span>
            )}
            {p.pl_esi && (
              <span className="esi-badge">ESI: {p.pl_esi}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ResultGrid;