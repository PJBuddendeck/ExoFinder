import React from 'react';
import ExoplanetSearch from './components/home/ExoplanetSearch';

function App() {
  return (
    <div>
      <header>
        <h1>Exoplanet Data Explorer</h1>
      </header>

      <main>
        <ExoplanetSearch />
      </main>

      <footer>
        <hr />
        <p>Source: NASA Exoplanet Archive</p>
      </footer>
    </div>
  );
}

export default App;