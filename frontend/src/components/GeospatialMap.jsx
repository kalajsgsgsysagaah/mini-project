import React from 'react';

const GeospatialMap = ({ geomorphology, stations, selectedStation, prediction }) => {
    // Manual positioning for the Telangana District Map image (telangana-map.jpg)
    // Values are in percentages relative to the image container
    const stationPositions = {
        "Bhadrachalam": { top: '65%', left: '82%', dist: 'Bhadradri-Kothagudem' },
        "Ramagundam NTPC": { top: '35%', left: '60%', dist: 'Peddapalli' },
        "Dowleswaram": { top: '75%', left: '92%', dist: 'Godavari Basin (East)' },
        "Pattiseema": { top: '70%', left: '90%', dist: 'Godavari Basin (East)' },
        "Rajahmundry": { top: '78%', left: '95%', dist: 'Godavari Basin (East)' },
    };

    const getZoneColor = (zone) => {
        const colors = {
            'Very High Potential Zone': '#4ecdc4',
            'High Potential Zone': '#1a73e8',
            'Moderate Potential Zone': '#ffd700',
            'Low Potential Zone': '#ff6b6b',
            'Very Low Potential Zone': '#ff4040',
            'Very High': '#4ecdc4',
            'High': '#1a73e8',
            'Moderate': '#ffd700',
            'Low': '#ff6b6b',
            'Very Low': '#ff4040'
        };
        return colors[zone] || '#1a73e8';
    };

    return (
        <div className="geospatial-map-container image-map-view" style={{
            position: 'relative',
            width: '100%',
            borderRadius: '12px',
            overflow: 'hidden',
            border: '2px solid rgba(255,255,255,0.1)',
            background: '#fff'
        }}>
            {/* The Telangana District Map Image */}
            <img
                src="/telangana-map.jpg"
                alt="Telangana Map"
                style={{ width: '100%', display: 'block', opacity: 0.9 }}
            />

            {/* Overlay Station Dots */}
            {Object.entries(stations).map(([name, info]) => {
                const pos = stationPositions[name] || { top: '50%', left: '50%' };
                const isSelected = name === selectedStation;
                const zone = isSelected && prediction ? prediction.predicted_zone : info.groundwater_zone;
                const color = getZoneColor(zone);

                return (
                    <div
                        key={name}
                        style={{
                            position: 'absolute',
                            top: pos.top,
                            left: pos.left,
                            transform: 'translate(-50%, -50%)',
                            zIndex: isSelected ? 100 : 10,
                            cursor: 'help'
                        }}
                    >
                        {/* Pulse for selected station */}
                        {isSelected && (
                            <div style={{
                                position: 'absolute',
                                width: '30px',
                                height: '30px',
                                background: color,
                                borderRadius: '50%',
                                opacity: 0.3,
                                left: '-10px',
                                top: '-10px',
                                animation: 'pulse 1.5s infinite ease-out'
                            }}></div>
                        )}
                        <div style={{
                            width: isSelected ? '14px' : '10px',
                            height: isSelected ? '14px' : '10px',
                            background: color,
                            border: `2px solid ${isSelected ? '#ffd700' : '#fff'}`,
                            borderRadius: '50%',
                            boxShadow: '0 0 5px rgba(0,0,0,0.5)',
                            transition: 'all 0.3s ease'
                        }}></div>

                        {/* Label */}
                        <div style={{
                            position: 'absolute',
                            left: '15px',
                            top: isSelected ? '-5px' : '0',
                            background: isSelected ? 'rgba(13, 21, 48, 0.95)' : 'rgba(255,255,255,0.85)',
                            color: isSelected ? '#ffd700' : '#000',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontSize: '9px',
                            fontWeight: 'bold',
                            whiteSpace: 'nowrap',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                            zIndex: 101,
                            border: isSelected ? '1px solid #ffd700' : 'none'
                        }}>
                            {name}
                        </div>
                    </div>
                );
            })}

            {/* Map Legends Title */}
            <div style={{
                position: 'absolute',
                top: '10px',
                left: '10px',
                background: 'rgba(255,255,255,0.9)',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '10px',
                fontWeight: 'bold',
                color: '#111',
                border: '1px solid #ccc'
            }}>
                🛰️ GODAVARI BASIN MONITORING
            </div>

            {/* Potential Scale */}
            <div style={{
                position: 'absolute',
                bottom: '10px',
                right: '10px',
                background: 'rgba(255,255,255,0.95)',
                padding: '8px',
                borderRadius: '8px',
                fontSize: '9px',
                border: '1px solid #ddd',
                color: '#333'
            }}>
                <div style={{ fontWeight: 'bold', marginBottom: '4px', borderBottom: '1px solid #eee' }}>Zones</div>
                {[
                    { label: 'Very High', color: '#4ecdc4' },
                    { label: 'High', color: '#1a73e8' },
                    { label: 'Moderate', color: '#ffd700' },
                    { label: 'Low', color: '#ff6b6b' },
                ].map(item => (
                    <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '2px' }}>
                        <div style={{ width: '8px', height: '8px', background: item.color, borderRadius: '50%' }}></div>
                        <div>{item.label}</div>
                    </div>
                ))}
            </div>

            <style>{`
                @keyframes pulse {
                    0% { transform: scale(0.95); opacity: 0.7; }
                    100% { transform: scale(2.5); opacity: 0; }
                }
            `}</style>
        </div>
    );
};

export default GeospatialMap;
