import React from 'react';
import ExoplanetSearch from './components/ExoplanetSearch/ExoplanetSearch';
import Header from './components/Header/Header';
import Footer from './components/Footer/Footer';

function App() {
  return (
    <div>
      <header>
        <Header />
      </header>

      <main>
        <ExoplanetSearch />
      </main>

      <footer>
        <Footer />
      </footer>
    </div>
  );
}

export default App;