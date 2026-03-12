import React, { useState, useEffect } from 'react';

const HistoryTab = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = () => {
        setLoading(true);
        fetch('/api/history')
            .then(res => res.json())
            .then(data => {
                setHistory(data.history || []);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching history:", err);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    if (loading && history.length === 0) return <div className="loading-spinner">Loading history...</div>;

    return (
        <div className="tab-content history-tab">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <div>
                    <h2>📜 Prediction History (SQL Store)</h2>
                    <p className="tab-description">All historical predictions stored in the local SQLite database.</p>
                </div>
                <button
                    className="btn-primary"
                    style={{ width: 'auto', padding: '8px 20px', fontSize: '0.8rem', marginTop: 0 }}
                    onClick={fetchHistory}
                    disabled={loading}
                >
                    {loading ? '⌛ Refreshing...' : '🔄 Refresh'}
                </button>
            </div>

            {history.length === 0 ? (
                <div className="no-data">No history found. Try making a prediction!</div>
            ) : (
                <div className="history-table-container">
                    <table className="history-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Station/Geology</th>
                                <th>Zone</th>
                                <th>Confidence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.map((item, idx) => {
                                const probs = typeof item.probabilities === 'string'
                                    ? JSON.parse(item.probabilities.replace(/'/g, '"'))
                                    : item.probabilities;

                                const topProb = probs ? Math.max(...Object.values(probs)) : 0;

                                return (
                                    <tr key={idx}>
                                        <td>{new Date(item.timestamp).toLocaleString()}</td>
                                        <td>
                                            <strong>{item.geology}</strong>
                                            <br />
                                            <small>{item.lulc} | {item.soil}</small>
                                        </td>
                                        <td>
                                            <span className={`zone-badge ${item.predicted_zone.toLowerCase().replace(/ /g, '-')}`}>
                                                {item.predicted_zone}
                                            </span>
                                        </td>
                                        <td>{(topProb * 100).toFixed(1)}%</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default HistoryTab;
