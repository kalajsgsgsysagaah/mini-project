import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Download } from 'lucide-react';
import GeospatialMap from './GeospatialMap';


const PredictTab = ({ stations, selectedStation, setSelectedStation, setLivePrediction, setHistory, fetchHistory }) => {
    const [formData, setFormData] = useState({
        geology: 'Basalt',
        geomorphology: 'Flood Plain',
        soil: 'Alluvial',
        slope_percent: 15,
        drainage_density: 2.5,
        lineament_density: 0.5,
        lulc: 'Agriculture',
        ndvi: 0.4,
        savi: 0.3,
        rainfall_mm: 800
    });

    const [meta, setMeta] = useState({
        geology: [],
        geomorphology: [],
        soil: [],
        lulc: []
    });

    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetch('/api/meta')
            .then(res => res.json())
            .then(data => setMeta(data))
            .catch(err => console.error("Error fetching meta:", err));
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: name.includes('density') || name.includes('percent') || name.includes('ndvi') || name.includes('savi') || name.includes('rainfall') ? parseFloat(value) : value }));
    };

    // 🔄 Sync inputs when station changes
    useEffect(() => {
        if (selectedStation && stations[selectedStation]) {
            const station = stations[selectedStation];

            // Map station metadata to form fields
            const matchedGeology = meta.geology.find(g => station.geological_formation?.includes(g)) || formData.geology;
            const matchedSoil = meta.soil.find(s => station.soil_type?.includes(s)) || formData.soil;
            const matchedGeomorph = meta.geomorphology.find(g => station.description?.includes(g)) || formData.geomorphology;
            const matchedLulc = meta.lulc.find(l => station.description?.toLowerCase().includes(l.toLowerCase())) || formData.lulc;

            // Parse rainfall from recharge rate (e.g., "500-750 mm/year" -> 625)
            let rainfall = formData.rainfall_mm;
            const rfMatch = station.recharge_rate?.match(/(\d+)-(\d+)/);
            if (rfMatch) {
                rainfall = (parseInt(rfMatch[1]) + parseInt(rfMatch[2])) / 2;
            }

            setFormData(prev => ({
                ...prev,
                geology: matchedGeology,
                soil: matchedSoil,
                geomorphology: matchedGeomorph,
                lulc: matchedLulc,
                rainfall_mm: rainfall
            }));
        }
    }, [selectedStation, stations, meta.geology, meta.soil, meta.geomorphology, meta.lulc]);

    const handlePredict = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...formData, station: selectedStation })
            });
            const data = await res.json();
            setPrediction(data);
            setLivePrediction(data.predicted_zone);

            // Dynamically add the response to history state so it's instantly available in HistoryTab
            const newHistoryRecord = {
                timestamp: new Date().toISOString(),
                geology: formData.geology,
                geomorphology: formData.geomorphology,
                soil: formData.soil,
                slope_percent: formData.slope_percent,
                drainage_density: formData.drainage_density,
                lineament_density: formData.lineament_density,
                lulc: formData.lulc,
                ndvi: formData.ndvi,
                savi: formData.savi,
                rainfall_mm: formData.rainfall_mm,
                predicted_zone: data.predicted_zone,
                probabilities: data.probabilities,
                station: selectedStation
            };

            if (setHistory) {
                setHistory(prev => [newHistoryRecord, ...prev]);
            }
            if (fetchHistory) {
                // optionally re-fetch from backend to make sure id is updated
                setTimeout(fetchHistory, 500); 
            }
        } catch (err) {
            console.error("Prediction error:", err);
        } finally {
            setLoading(false);
        }
    };

    const downloadCSV = () => {
        if (!prediction) return;

        // Dataset-like format: Headers are param names, values are one row
        const headers = [
            "Station", "Geology", "Geomorphology", "Soil", "Slope", "Drainage", "Lineament", "LULC", "NDVI", "SAVI", "Rainfall", "Predicted_Zone"
        ];

        const row = [
            selectedStation,
            formData.geology,
            formData.geomorphology,
            formData.soil,
            formData.slope_percent,
            formData.drainage_density,
            formData.lineament_density,
            formData.lulc,
            formData.ndvi,
            formData.savi,
            formData.rainfall_mm,
            prediction.predicted_zone
        ];

        const csvContent = "data:text/csv;charset=utf-8,"
            + headers.join(",") + "\n"
            + row.join(",");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `groundwater_response_${selectedStation.replace(/\s+/g, '_')}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
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

    const chartData = prediction ? Object.entries(prediction.probabilities).map(([name, value]) => ({
        name,
        probability: value,
        fill: getZoneColor(name)
    })).sort((a, b) => {
        const order = { 'Very Low': 0, 'Low': 1, 'Moderate': 2, 'High': 3, 'Very High': 4 };
        return order[a.name] - order[b.name];
    }) : [];

    return (
        <div className="grid-2" style={{ alignItems: 'start' }}>
            <div className="card" style={{ maxHeight: '90vh', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
                <div style={{ flex: 1 }}>
                    <div className="section-title">📍 Select Station</div>
                    <div className="form-group">
                        <label>Station (Location)</label>
                        <select
                            value={selectedStation}
                            onChange={(e) => setSelectedStation(e.target.value)}
                        >
                            {Object.keys(stations).map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                    </div>

                    <div className="section-title" style={{ marginTop: '20px' }}>🌍 10 Hydro-Geological Inputs</div>
                    <div className="grid-2" style={{ gap: '10px' }}>
                        <div className="form-group">
                            <label>Geology</label>
                            <select name="geology" value={formData.geology} onChange={handleChange}>
                                {meta.geology.map(g => <option key={g} value={g}>{g}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Geomorphology</label>
                            <select name="geomorphology" value={formData.geomorphology} onChange={handleChange}>
                                {meta.geomorphology.map(g => <option key={g} value={g}>{g}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="grid-2" style={{ gap: '10px' }}>
                        <div className="form-group">
                            <label>Soil Type</label>
                            <select name="soil" value={formData.soil} onChange={handleChange}>
                                {meta.soil.map(s => <option key={s} value={s}>{s}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Land Use (LULC)</label>
                            <select name="lulc" value={formData.lulc} onChange={handleChange}>
                                {meta.lulc.map(l => <option key={l} value={l}>{l}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="section-title" style={{ marginTop: '10px', fontSize: '0.8rem' }}>📐 Numerical Parameters</div>
                    <div className="grid-2" style={{ gap: '10px' }}>
                        <div className="form-group">
                            <label>Slope (%): {formData.slope_percent}</label>
                            <input type="range" name="slope_percent" min="0" max="50" step="0.1" value={formData.slope_percent} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label>Rainfall (mm): {formData.rainfall_mm}</label>
                            <input type="range" name="rainfall_mm" min="0" max="3000" step="1" value={formData.rainfall_mm} onChange={handleChange} />
                        </div>
                    </div>

                    <div className="grid-2" style={{ gap: '10px' }}>
                        <div className="form-group">
                            <label>Drainage Density: {formData.drainage_density}</label>
                            <input type="range" name="drainage_density" min="0" max="10" step="0.1" value={formData.drainage_density} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label>Lineament Density: {formData.lineament_density}</label>
                            <input type="range" name="lineament_density" min="0" max="5" step="0.1" value={formData.lineament_density} onChange={handleChange} />
                        </div>
                    </div>

                    <div className="grid-2" style={{ gap: '10px' }}>
                        <div className="form-group">
                            <label>NDVI: {formData.ndvi}</label>
                            <input type="range" name="ndvi" min="-1" max="1" step="0.01" value={formData.ndvi} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label>SAVI: {formData.savi}</label>
                            <input type="range" name="savi" min="-1" max="1" step="0.01" value={formData.savi} onChange={handleChange} />
                        </div>
                    </div>
                </div>

                <button
                    className="btn-primary"
                    onClick={handlePredict}
                    disabled={loading}
                    style={{
                        marginTop: '20px',
                        position: 'sticky',
                        bottom: '0',
                        zIndex: 10,
                        background: '#1a73e8',
                        boxShadow: '0 4px 14px rgba(26, 115, 232, 0.3)'
                    }}
                >
                    {loading ? 'Processing...' : '🔍 Analyse Groundwater Potential'}
                </button>
            </div>

            <div className="card" style={{ position: 'sticky', top: '20px' }}>
                <div className="section-title">🗺️ Geospatial Analysis</div>

                {/* Always show the map */}
                <GeospatialMap
                    geomorphology={formData.geomorphology || 'Flood Plain'}
                    stations={stations}
                    selectedStation={selectedStation}
                    prediction={prediction}
                />

                <div className="gw-divider" style={{ width: '100%', margin: '20px 0', opacity: 0.3 }}></div>

                <div className="section-title">📊 Prediction Results</div>
                {prediction ? (
                    <>
                        <div className="result-box" style={{ background: `rgba(${getZoneColor(prediction.predicted_zone) === '#ffd700' ? '255,215,0' : '26,115,232'}, 0.1)` }}>
                            🌍 {prediction.predicted_zone}
                        </div>

                        <div style={{ height: '280px', marginBottom: '20px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(102,126,234,0.1)" />
                                    <XAxis dataKey="name" stroke="#7a8ab0" fontSize={10} />
                                    <YAxis stroke="#7a8ab0" fontSize={10} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0d1530', border: '1px solid #1a73e8', borderRadius: '10px' }}
                                        itemStyle={{ color: '#c8d8ff' }}
                                    />
                                    <Bar dataKey="probability">
                                        {chartData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.fill} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        <button
                            className="btn-primary"
                            onClick={downloadCSV}
                            style={{
                                background: 'rgba(78,205,196,0.1)',
                                color: '#4ecdc4',
                                border: '1px solid #4ecdc4',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '8px',
                                boxShadow: 'none'
                            }}
                        >
                            <Download size={18} /> Download CSV Dataset Row
                        </button>

                    </>
                ) : (
                    <div style={{ textAlign: 'center', color: '#7a8ab0', padding: '50px' }}>
                        Configure the 10 parameters and click "Analyse"
                    </div>
                )}
            </div>
        </div>
    );
};

export default PredictTab;
