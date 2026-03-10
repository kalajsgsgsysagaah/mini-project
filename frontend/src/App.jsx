import React, { useState, useEffect } from 'react';
import './index.css';

// Components
import PredictTab from './components/PredictTab';
import MapTab from './components/MapTab';
import DashboardTab from './components/DashboardTab';
import AccuracyTab from './components/AccuracyTab';

function App() {
  const [activeTab, setActiveTab] = useState('prediction');
  const [stations, setStations] = useState({});
  const [selectedStation, setSelectedStation] = useState('');
  const [livePrediction, setLivePrediction] = useState(null);

  useEffect(() => {
    fetch('/api/stations')
      .then(res => res.json())
      .then(data => {
        setStations(data.stations);
        setSelectedStation(Object.keys(data.stations)[0]);
      })
      .catch(err => console.error("Error fetching stations:", err));
  }, []);

  return (
    <div className="app-container">
      <header className="gw-header">
        <h1>💧 GROUNDWATER POTENTIAL ZONING</h1>
        <p>Geospatial Analysis · Random Forest · Godavari Basin · Telangana</p>
        <div className="gw-divider"></div>
      </header>

      <nav>
        <ul className="tabs-nav">
          <li>
            <button
              className={activeTab === 'prediction' ? 'active' : ''}
              onClick={() => setActiveTab('prediction')}
            >
              🔍 Prediction
            </button>
          </li>
          <li>
            <button
              className={activeTab === 'map' ? 'active' : ''}
              onClick={() => setActiveTab('map')}
            >
              🗺️ Geospatial Map
            </button>
          </li>
          <li>
            <button
              className={activeTab === 'dashboard' ? 'active' : ''}
              onClick={() => setActiveTab('dashboard')}
            >
              🌊 Godavari Dashboard
            </button>
          </li>
          <li>
            <button
              className={activeTab === 'accuracy' ? 'active' : ''}
              onClick={() => setActiveTab('accuracy')}
            >
              🎯 Model Accuracy
            </button>
          </li>
        </ul>
      </nav>

      <main>
        {activeTab === 'prediction' && (
          <PredictTab
            stations={stations}
            selectedStation={selectedStation}
            setSelectedStation={setSelectedStation}
            setLivePrediction={setLivePrediction}
          />
        )}
        {activeTab === 'map' && (
          <MapTab
            selectedStation={selectedStation}
            setSelectedStation={setSelectedStation}
            stations={stations}
            livePrediction={livePrediction}
          />
        )}
        {activeTab === 'dashboard' && (
          <DashboardTab
            selectedStation={selectedStation}
            setSelectedStation={setSelectedStation}
            stations={stations}
            livePrediction={livePrediction}
          />
        )}
        {activeTab === 'accuracy' && <AccuracyTab />}
      </main>

      <footer className="gw-footer">
        <span>🌊 Groundwater ML · Godavari Basin</span>
      </footer>
    </div>
  );
}

export default App;
