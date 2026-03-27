import React, { useState, useEffect } from 'react';
import './ExoplanetSearch.css';
import ResultGrid from '../ResultGrid/ResultGrid'

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

      <ResultGrid 
          planets={planets}
        />
    </div>
  );
};

export default ExoplanetSearch;