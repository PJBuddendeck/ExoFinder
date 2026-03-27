import React, { useState, useEffect } from 'react';
import './ExoplanetSearch.css';
import ResultGrid from '../ResultGrid/ResultGrid';
import PlanetDashboard from '../PlanetDashboard/PlanetDashboard';

const ExoplanetSearch = () => {
  const [planets, setPlanets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedPlanet, setSelectedPlanet] = useState(null);
  
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('sy_dist'); 
  const [sortOrder, setSortOrder] = useState('asc');
  const [filterMenu, setFilterMenu] = useState(false);

  useEffect(() => {
    if (sortBy === 'pl_esi' && sortOrder !== 'desc') {
      setSortOrder('desc');
    }
  }, [sortBy, sortOrder]);

  useEffect(() => {
    const fetchPlanets = async () => {
      setLoading(true);
      try {
        // We pass the sort parameters to your API
        const url = `/api/planets?search=${encodeURIComponent(search)}&sort=${sortBy}&order=${sortOrder}`;
        const res = await fetch(url);
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
  }, [search, sortBy, sortOrder]); // Re-run when search OR sort changes

  return (
    <div id="search-container">
      <div className="controls-row">
        <input 
          id="search-input"
          type="text" 
          placeholder="Search planets..." 
          value={search} 
          onChange={(e) => setSearch(e.target.value)} 
        />
        <button onClick={(e) => setFilterMenu(!filterMenu)}>Sort/Filter</button>
      </div>
      <div className={`filters-row ${filterMenu ? 'is-open' : ''}`}>
        <div className="filter-group">
          {/* Dropdown 1: The Field */}
          <select 
            className="filter-dropdown"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="sy_dist">Distance</option>
            <option value="pl_bmasse">Mass</option>
            <option value="pl_rade">Radius</option>
            <option value="disc_year">Discovery Year</option>
            <option value="pl_eqt">Temperature (EQT)</option>
            <option value="pl_esi">ESI</option>
          </select>

          {/* Dropdown 2: The Direction */}
          <select 
            className={`filter-dropdown ${sortBy === 'pl_esi' ? 'is-disabled' : ''}`}
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
            disabled={sortBy === 'pl_esi'}
          >
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </div>
      </div>

      {loading ? <p className="loading-text">Scanning deep space...</p> : (
        <ResultGrid 
          planets={planets}
          onPlanetClick={(planet) => setSelectedPlanet(planet)}
        />
      )}

      {selectedPlanet && (
        <PlanetDashboard 
          planet={selectedPlanet} 
          onClose={() => setSelectedPlanet(null)} 
        />
      )}
    </div>
  );
};

export default ExoplanetSearch;