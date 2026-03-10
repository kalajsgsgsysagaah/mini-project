import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix for default marker icons
const icon = L.icon({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

function ChangeView({ center, zoom }) {
    const map = useMap();
    useEffect(() => {
        if (center && center[0] && center[1]) {
            map.flyTo(center, zoom);
        }
    }, [center, zoom, map]);
    return null;
}

const MapTab = ({ selectedStation, setSelectedStation, stations, livePrediction }) => {
    const stationList = Object.entries(stations);
    const selectedData = stations[selectedStation] || { lat: 17.5, lon: 80 };

    return (
        <div className="grid-2" style={{ gridTemplateColumns: '1.5fr 1fr' }}>
            <div className="card" style={{ padding: '0', overflow: 'hidden', height: '600px', position: 'relative' }}>
                <div className="section-title" style={{ position: 'absolute', top: '15px', left: '15px', zIndex: 1000, background: 'rgba(13,21,48,0.8)', padding: '5px 10px', borderRadius: '5px' }}>
                    🛰️ Exact Station Locations
                </div>
                <MapContainer center={[selectedData.lat, selectedData.lon]} zoom={8} style={{ height: '100%', width: '100%' }}>
                    <ChangeView center={[selectedData.lat, selectedData.lon]} zoom={10} />
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    {stationList.map(([name, info]) => {
                        const isSelected = name === selectedStation;
                        const zone = isSelected && livePrediction ? livePrediction : info.groundwater_zone;

                        return (
                            <Marker
                                key={name}
                                position={[info.lat, info.lon]}
                                icon={icon}
                                eventHandlers={{
                                    click: () => setSelectedStation(name),
                                }}
                            >
                                <Popup>
                                    <div style={{ color: '#060b18', padding: '5px', fontWeight: 'bold' }}>
                                        <div style={{ color: '#1a73e8', fontSize: '1.1rem' }}>{name}</div>
                                        <div style={{ color: '#0d1530', marginTop: '5px' }}>Zone: {zone}</div>
                                        {isSelected && livePrediction && <div style={{ color: '#accent2', fontSize: '0.8rem' }}>(Live Updated)</div>}
                                    </div>
                                </Popup>
                            </Marker>
                        );
                    })}
                </MapContainer>
            </div>

            <div className="card" style={{ height: '600px', overflowY: 'auto' }}>
                <div className="section-title">📍 Stations Summary</div>
                <table style={{ fontSize: '0.75rem' }}>
                    <thead>
                        <tr>
                            <th>Station</th>
                            <th>Live Zone</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {stationList.map(([name, info]) => {
                            const isSelected = name === selectedStation;
                            const zone = isSelected && livePrediction ? livePrediction : info.groundwater_zone;

                            return (
                                <tr
                                    key={name}
                                    style={{
                                        cursor: 'pointer',
                                        ...(isSelected ? { background: 'rgba(26, 115, 232, 0.3)', borderLeft: '4px solid #ffd700' } : {})
                                    }}
                                    onClick={() => setSelectedStation(name)}
                                >
                                    <td style={{ color: isSelected ? '#ffd700' : '#c8d8ff', fontWeight: 'bold' }}>
                                        {isSelected ? '⭐ ' + name : name}
                                    </td>
                                    <td style={{ color: isSelected ? '#ffd700' : '#4ecdc4', fontWeight: isSelected ? 'bold' : 'normal' }}>
                                        {zone}
                                    </td>
                                    <td style={{ color: '#7a8ab0' }}>Active</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default MapTab;
