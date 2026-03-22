import React, { useState, useEffect, memo } from 'react';
import './Footer.css';
import '../style.css';

const Footer = memo(() => {
  const [syncTime, setSyncTime] = useState('Fetching...');

  useEffect(() => {
    const getStatus = async () => {
      try {
        const res = await fetch('/api/sync-status');
        const data = await res.json();
        if (data.last_sync) {
          const date = new Date(data.last_sync);
          setSyncTime(date.toLocaleString());
        }
      } catch (err) {
        setSyncTime('Error reaching server');
      }
    };
    getStatus();
  }, []);

  return (
    <footer className="footer-container">
      <p>This website has made use of the <a href="https://exoplanetarchive.ipac.caltech.edu/" target="_blank" rel="noopener noreferrer">NASA Exoplanet Archive</a>, which is operated by the California Institute of Technology, 
        under contract with the National Aeronautics and Space Administration under the Exoplanet Exploration Program.</p>
      <p>The Planetary Systems Composite Parameters Table DOI can be found <a href="https://doi.org/10.26133/NEA13" target="_blank" rel="noopener noreferrer">here</a>.
        Data was last synced on: <span id="last-sync">{syncTime}</span>.</p>
      <p>Created by <a href="https://pjbuddendeck.github.io/" target="_blank" rel="noopener noreferrer">Peter Buddendeck</a>. Please visit this <a href="https://pjbuddendeck.github.io/#/contact" target="_blank" rel="noopener noreferrer">contact page</a> for any questions or feedback.</p>
    </footer>
  );
});

export default Footer;