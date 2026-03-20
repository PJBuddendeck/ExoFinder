import React, { useState, useEffect } from 'react';

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
    <div>
      <input 
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
            <th>Equilibrium Temp (K)</th>  
          </tr>
        </thead>
        <tbody>
          {planets.map((p, i) => (
            <tr key={i}>
              <td>{p.pl_name}</td>
              <td>{p.hostname}</td>
              <td>{p.disc_year}</td>
              <td>{p.sy_dist}</td>
              <td>{p.pl_eqt !== null && p.pl_eqt !== undefined ? p.pl_eqt : "Unknown"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ExoplanetSearch;