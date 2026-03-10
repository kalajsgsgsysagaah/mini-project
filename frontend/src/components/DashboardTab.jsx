import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

const icon = L.icon({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// Clean mapping of station names to assets
const stationImages = {
    "Bhadrachalam": "/assets/Bhadrachalam.png",
    "Ramagundam NTPC": "/assets/Ramagundam.png",
    "Dowleswaram": "/assets/Dowleswaram.png",
    "Pattiseema": "/assets/Pattiseema.png",
    "Rajahmundry": "/assets/Rajahmundry.png"
};

function ChangeView({ center, zoom }) {
    const map = useMap();
    useEffect(() => {
        if (center && center[0] && center[1]) {
            map.flyTo(center, zoom);
        }
    }, [center, zoom, map]);
    return null;
}

const DashboardTab = ({ selectedStation, setSelectedStation, stations, livePrediction }) => {
    const [subTab, setSubTab] = useState('map');
    const stationList = Object.entries(stations);
    const chartData = stationList.map(([name, info]) => ({
        name: name,
        avg: info.avg_discharge,
        peak: info.peak_discharge,
        min: info.min_discharge,
        depth: info.depth_to_water,
        level: info.current_level,
        zone: name === selectedStation && livePrediction ? livePrediction : info.groundwater_zone
    }));

    const selectedData = stations[selectedStation] || { lat: 17.5, lon: 80 };
    const stationImg = stationImages[selectedStation] || stationImages["Bhadrachalam"];

    const renderSubTab = () => {
        switch (subTab) {
            case 'map':
                return (
                    <div className="card" style={{ padding: '0', overflow: 'hidden', height: '500px', border: '2px solid var(--accent1)' }}>
                        <MapContainer center={[selectedData.lat, selectedData.lon]} zoom={8} style={{ height: '100%', width: '100%' }}>
                            <ChangeView center={[selectedData.lat, selectedData.lon]} zoom={10} />
                            <TileLayer
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            />
                            {stationList.map(([name, info]) => (
                                <Marker
                                    key={name}
                                    position={[info.lat, info.lon]}
                                    icon={icon}
                                    eventHandlers={{
                                        click: () => setSelectedStation(name),
                                    }}
                                >
                                    <Popup>
                                        <div style={{ color: '#060b18', padding: '5px' }}>
                                            <h3 style={{ margin: '0 0 5px', color: '#667eea' }}>{name}</h3>
                                            <p style={{ color: '#0d1530', fontWeight: 'bold' }}>
                                                <b>Zone:</b> {name === selectedStation && livePrediction ? livePrediction : info.groundwater_zone}
                                            </p>
                                            <button
                                                className="btn-primary"
                                                style={{ padding: '5px 12px', fontSize: '0.75rem', width: 'auto', marginTop: '10px', background: '#667eea' }}
                                                onClick={() => { setSelectedStation(name); setSubTab('details'); }}
                                            >
                                                Deep Dive Details
                                            </button>
                                        </div>
                                    </Popup>
                                </Marker>
                            ))}
                        </MapContainer>
                    </div>
                );
            case 'discharge':
                return (
                    <div className="card">
                        <div className="section-title">⚡ Water Discharge Analysis (MCM)</div>
                        <div style={{ height: '400px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(102,126,234,0.1)" />
                                    <XAxis dataKey="name" stroke="#7a8ab0" fontSize={11} />
                                    <YAxis stroke="#7a8ab0" />
                                    <Tooltip contentStyle={{ backgroundColor: '#0d1530', border: '1px solid #667eea' }} />
                                    <Legend />
                                    <Bar dataKey="avg" name="Average" fill="#667eea" onClick={(data) => setSelectedStation(data.name)} style={{ cursor: 'pointer' }} />
                                    <Bar dataKey="peak" name="Peak" fill="#4ecdc4" onClick={(data) => setSelectedStation(data.name)} style={{ cursor: 'pointer' }} />
                                    <Bar dataKey="min" name="Minimum" fill="#ff6b6b" onClick={(data) => setSelectedStation(data.name)} style={{ cursor: 'pointer' }} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                );
            case 'gw':
                return (
                    <div className="card">
                        <div className="section-title">🔬 Groundwater Parameter Projections</div>
                        <div style={{ height: '400px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(102,126,234,0.1)" />
                                    <XAxis dataKey="name" stroke="#7a8ab0" fontSize={11} />
                                    <YAxis stroke="#7a8ab0" />
                                    <Tooltip contentStyle={{ backgroundColor: '#0d1530', border: '1px solid #667eea' }} />
                                    <Legend />
                                    <Line type="monotone" dataKey="depth" name="Depth to Water (m)" stroke="#ff6b6b" strokeWidth={2} />
                                    <Line type="monotone" dataKey="level" name="Water Level (m)" stroke="#ffd700" strokeDasharray="5 5" />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                );
            case 'details':
                return (
                    <div className="card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                            <div className="section-title" style={{ marginBottom: 0 }}>📍 Station Deep-Dive</div>
                            <select
                                value={selectedStation}
                                onChange={(e) => setSelectedStation(e.target.value)}
                                style={{ width: '200px', background: 'rgba(102,126,234,0.1)', border: '1px solid var(--accent1)', color: '#ffd700', fontWeight: 'bold' }}
                            >
                                {stationList.map(([name]) => <option key={name} value={name} style={{ color: '#060b18' }}>{name}</option>)}
                            </select>
                        </div>

                        <div style={{ marginBottom: '20px', borderRadius: '15px', overflow: 'hidden', height: '280px', border: '1px solid var(--border)', background: '#0a0f1e' }}>
                            <img
                                key={selectedStation}
                                src={stationImg}
                                alt={selectedStation}
                                style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: 0.9, transition: 'opacity 0.5s' }}
                            />
                        </div>

                        <div className="card" style={{ background: 'rgba(102,126,234,0.05)', marginBottom: '20px', border: '1px dashed var(--accent1)' }}>
                            <p style={{ fontStyle: 'italic', color: '#c8d8ff', lineHeight: '1.6' }}>
                                "{selectedData.description || 'Monitoring core groundwater levels and recharge patterns across the Godavari basin.'}"
                            </p>
                        </div>

                        <div className="grid-2">
                            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '12px', border: '1px solid rgba(102,126,234,0.2)' }}>
                                <h3 style={{ color: '#4ecdc4', fontSize: '14px', marginBottom: '10px' }}>⚡ Water Metrics</h3>
                                <p><b>Avg Discharge:</b> {selectedData.avg_discharge} MCM</p>
                                <p><b>Peak Discharge:</b> {selectedData.peak_discharge} MCM</p>
                                <p><b>Min Discharge:</b> {selectedData.min_discharge} MCM</p>
                            </div>
                            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '12px', border: '1px solid rgba(102,126,234,0.2)' }}>
                                <h3 style={{ color: '#667eea', fontSize: '14px', marginBottom: '10px' }}>🌍 Zone Detail</h3>
                                <p style={{ color: '#ffd700', fontWeight: 'bold', fontSize: '1.2rem' }}>
                                    {selectedStation === selectedStation && livePrediction ? livePrediction : selectedData.groundwater_zone}
                                </p>
                                <p><b>Water Quality:</b> {selectedData.water_quality}</p>
                                <p><b>Yield Potential:</b> {selectedData.yield_potential}</p>
                            </div>
                        </div>
                    </div>
                );
            case 'summary':
                return (
                    <div className="card">
                        <div className="section-title">📋 All Stations Recap</div>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ border: '1px solid var(--border)' }}>
                                <thead>
                                    <tr style={{ background: 'var(--accent1)' }}>
                                        <th>Station</th>
                                        <th>Avg (MCM)</th>
                                        <th>Zone</th>
                                        <th>Quality</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {chartData.map(row => (
                                        <tr
                                            key={row.name}
                                            style={{
                                                cursor: 'pointer',
                                                ...(row.name === selectedStation ? { background: 'rgba(102,126,234,0.25)', borderLeft: '4px solid #ffd700' } : {})
                                            }}
                                            onClick={() => setSelectedStation(row.name)}
                                        >
                                            <td>{row.name === selectedStation ? '⭐ ' + row.name : row.name}</td>
                                            <td>{row.avg}</td>
                                            <td style={{ color: row.name === selectedStation ? '#ffd700' : '#4ecdc4', fontWeight: 'bold' }}>{row.zone}</td>
                                            <td>{stations[row.name].water_quality}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div>
            <ul className="tabs-nav" style={{ marginBottom: '10px', background: 'rgba(102,126,234,0.1)', border: '1.5px solid var(--accent1)' }}>
                <li><button className={subTab === 'map' ? 'active' : ''} onClick={() => setSubTab('map')}>📍 Interactive Map</button></li>
                <li><button className={subTab === 'discharge' ? 'active' : ''} onClick={() => setSubTab('discharge')}>📊 Discharge Analysis</button></li>
                <li><button className={subTab === 'gw' ? 'active' : ''} onClick={() => setSubTab('gw')}>💧 GW Parameters</button></li>
                <li><button className={subTab === 'details' ? 'active' : ''} onClick={() => setSubTab('details')}>🔍 Station Details</button></li>
                <li><button className={subTab === 'summary' ? 'active' : ''} onClick={() => setSubTab('summary')}>📈 Summary Table</button></li>
            </ul>
            {renderSubTab()}
        </div>
    );
};

export default DashboardTab;
