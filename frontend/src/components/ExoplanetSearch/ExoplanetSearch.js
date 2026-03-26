import React, { useState, useEffect } from 'react';
import './ExoplanetSearch.css';

const ExoplanetSearch = () => {
  const [planets, setPlanets] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPlanets = async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/planets?search=${encodeURIComponent(search)}`);
        const data = await res.json();
        setPlanets(data);
      } catch (err) {
        console.error("Fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(fetchPlanets, 500);
    return () => clearTimeout(timer);
  }, [search]);

  const formatUnknown = (value) => {
    return value === null || value === undefined ? "Unknown" : value;
  };

  const formatDecimal = (value, dec) => {
    value = formatUnknown(value);
    if (value=='Unknown') return "Unknown";
    return Number(value).toFixed(dec);
  };

  return (
    <div id="search-container">
      <input 
        id="search-input"
        type="text" 
        placeholder="Search planets..." 
        value={search} 
        onChange={(e) => setSearch(e.target.value)} 
      />

      {loading && <p>Loading...</p>}

      <table border="1" style={{ marginTop: '20px', width: '100%' }}>
        <thead>
          <tr>
            <th>Planet Name</th>
            <th>Host Star</th>
            <th>Disc. Year</th>
            <th>Distance (Parsecs)</th>
            <th>Mass (Earth Masses)</th>
            <th>Radius (Earth Radii)</th>
            <th>Equilibrium Temp (K)</th>  
          </tr>
        </thead>
        <tbody>
          {planets.map((p, i) => (
            <tr key={i}>
              <td>{p.pl_name}</td>
              <td>{p.hostname}</td>
              <td>{formatUnknown(p.disc_year)}</td>
              <td>{formatDecimal(p.sy_dist, 3)}</td>
              <td>{formatDecimal(p.pl_bmasse, 3)}</td>
              <td>{formatDecimal(p.pl_rade, 3)}</td>
              <td>{formatDecimal(p.pl_eqt, 1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ExoplanetSearch;