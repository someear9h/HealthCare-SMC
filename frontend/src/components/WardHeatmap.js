import React, { useState, useEffect } from 'react';
import axios from 'axios';

const WardHeatmap = () => {
  const [wards, setWards] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWards = async () => {
      try {
        const res = await axios.get('http://localhost:8000/analytics/ward-risk');
        setWards(res.data.wards || []);
      } catch (error) {
        console.error('Error fetching wards:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWards();
  }, []);

  if (loading) {
    return <div className="flex justify-center p-4">Loading heatmap...</div>;
  }

  // Create fake grid layout (6 columns x 3 rows for now)
  const gridSize = 6;
  const maxRows = Math.ceil(wards.length / gridSize);

  // Sort by risk_score (descending) for visual impact
  const sortedWards = [...wards].sort((a, b) => b.risk_score - a.risk_score);

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'bg-red-600';
      case 'HIGH':
        return 'bg-orange-500';
      case 'MEDIUM':
        return 'bg-yellow-500';
      case 'LOW':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="bg-slate-800 p-6 rounded-lg mb-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">🗺️ Ward Risk Heatmap</h2>

      {sortedWards.length === 0 ? (
        <p className="text-gray-400">No wards data available.</p>
      ) : (
        <div className="space-y-4">
          {/* Heatmap Grid */}
          <div className={`grid gap-2 autogrid`} style={{ gridTemplateColumns: `repeat(${gridSize}, 1fr)` }}>
            {sortedWards.map((ward) => (
              <div
                key={ward.ward}
                className={`${getRiskColor(ward.risk_level)} p-4 rounded-lg cursor-pointer hover:scale-105 transition-transform shadow-lg`}
              >
                <p className="text-xs font-bold text-white truncate">{ward.ward}</p>
                <p className="text-lg font-bold text-white">{ward.risk_score.toFixed(1)}</p>
                <p className="text-xs text-white opacity-80">{ward.risk_level}</p>
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="flex gap-6 mt-6 pt-4 border-t border-slate-600">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span className="text-xs text-gray-300">LOW (0-25)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded"></div>
              <span className="text-xs text-gray-300">MEDIUM (25-50)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-orange-500 rounded"></div>
              <span className="text-xs text-gray-300">HIGH (50-75)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-600 rounded"></div>
              <span className="text-xs text-gray-300">CRITICAL (75+)</span>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-600">
            <div className="bg-slate-700 p-3 rounded">
              <p className="text-xs text-gray-400">Total Wards</p>
              <p className="text-2xl font-bold text-white">{wards.length}</p>
            </div>
            <div className="bg-red-900 p-3 rounded">
              <p className="text-xs text-gray-400">Critical</p>
              <p className="text-2xl font-bold text-red-400">
                {wards.filter((w) => w.risk_level === 'CRITICAL').length}
              </p>
            </div>
            <div className="bg-orange-900 p-3 rounded">
              <p className="text-xs text-gray-400">High Risk</p>
              <p className="text-2xl font-bold text-orange-400">
                {wards.filter((w) => w.risk_level === 'HIGH').length}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WardHeatmap;
