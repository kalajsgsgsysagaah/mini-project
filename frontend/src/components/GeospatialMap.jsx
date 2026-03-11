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
                            <>
                                <div style={{
                                    position: 'absolute',
                                    width: '40px',
                                    height: '40px',
                                    background: color,
                                    borderRadius: '50%',
                                    opacity: 0.4,
                                    left: '-12px',
                                    top: '-12px',
                                    animation: 'pulse 1.5s infinite ease-out'
                                }}></div>
                                <div style={{
                                    position: 'absolute',
                                    width: '60px',
                                    height: '60px',
                                    background: color,
                                    borderRadius: '50%',
                                    opacity: 0.2,
                                    left: '-22px',
                                    top: '-22px',
                                    animation: 'pulse 2s infinite ease-out',
                                    animationDelay: '0.5s'
                                }}></div>
                            </>
                        )}
                        <div style={{
                            width: isSelected ? '22px' : '16px',
                            height: isSelected ? '22px' : '16px',
                            background: color,
                            border: `3px solid ${isSelected ? '#ffd700' : '#fff'}`,
                            borderRadius: '50%',
                            boxShadow: '0 0 10px rgba(0,0,0,0.6)',
                            transition: 'all 0.3s ease',
                            animation: isSelected ? 'blink 0.8s infinite alternate' : 'none'
                        }}></div>

                        {/* Label */}
                        <div style={{
                            position: 'absolute',
                            left: isSelected ? '25px' : '20px',
                            top: isSelected ? '-8px' : '0',
                            background: isSelected ? '#1a73e8' : 'rgba(255,255,255,0.9)',
                            color: isSelected ? '#fff' : '#000',
                            padding: '3px 8px',
                            borderRadius: '6px',
                            fontSize: isSelected ? '11px' : '10px',
                            fontFamily: 'Orbitron, sans-serif',
                            fontWeight: 'bold',
                            whiteSpace: 'nowrap',
                            boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
                            zIndex: 101,
                            border: isSelected ? '2px solid #ffd700' : '1px solid #999',
                            animation: isSelected ? 'textBlink 0.8s infinite alternate' : 'none'
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
                background: 'rgba(255,255,255,0.95)',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '11px',
                fontFamily: 'Orbitron, sans-serif',
                fontWeight: 'bold',
                color: '#1a73e8',
                border: '2px solid #1a73e8',
                boxShadow: '0 4px 10px rgba(0,0,0,0.1)'
            }}>
                🛰️ STATION LIVE MONITORING
            </div>

            {/* Potential Scale */}
            <div style={{
                position: 'absolute',
                bottom: '10px',
                right: '10px',
                background: 'rgba(255,255,255,0.95)',
                padding: '10px',
                borderRadius: '10px',
                fontSize: '10px',
                border: '2px solid #ddd',
                color: '#333',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}>
                <div style={{ fontWeight: 'bold', marginBottom: '6px', borderBottom: '1px solid #eee', letterSpacing: '1px' }}>GROUNDWATER</div>
                {[
                    { label: 'Very High', color: '#4ecdc4' },
                    { label: 'High', color: '#1a73e8' },
                    { label: 'Moderate', color: '#ffd700' },
                    { label: 'Low', color: '#ff6b6b' },
                ].map(item => (
                    <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <div style={{ width: '10px', height: '10px', background: item.color, borderRadius: '50%', border: '1px solid #999' }}></div>
                        <div style={{ fontWeight: '600' }}>{item.label}</div>
                    </div>
                ))}
            </div>

            <style>{`
                @keyframes pulse {
                    0% { transform: scale(0.8); opacity: 0.6; }
                    100% { transform: scale(2.8); opacity: 0; }
                }
                @keyframes blink {
                    from { opacity: 1; transform: scale(1); }
                    to { opacity: 0.7; transform: scale(1.2); }
                }
                @keyframes textBlink {
                    from { transform: translateX(0); }
                    to { transform: translateX(3px); }
                }
            `}</style>
        </div>
    );
};

export default GeospatialMap;
