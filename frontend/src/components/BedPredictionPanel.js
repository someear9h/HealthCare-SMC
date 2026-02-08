import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BedPredictionPanel = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const res = await axios.get('http://localhost:8000/analytics/predicted-capacity');
        setPredictions(res.data.predictions || []);
      } catch (error) {
        console.error('Error fetching predictions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, []);

  if (loading) {
    return <div className="flex justify-center p-4">Loading predictions...</div>;
  }

  // Sort by beds_remaining_hours (ascending = crisis sooner)
  const sorted = [...predictions].sort((a, b) => a.beds_remaining_hours - b.beds_remaining_hours);
  const topAtRisk = sorted.slice(0, 8);

  return (
    <div className="bg-slate-800 p-6 rounded-lg mb-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">🔥 Bed Demand Prediction (Next 24h)</h2>
      
      {topAtRisk.length === 0 ? (
        <p className="text-gray-400">No facilities with predictions.</p>
      ) : (
        <div className="space-y-3">
          {topAtRisk.map((pred) => {
            // Handle null/undefined values
            const remainingHours = pred?.beds_remaining_hours ?? 24;
            const crisisLikely = pred?.crisis_likely === true;
            
            // Calculate bed usage percentage (inverse of remaining)
            // Higher usage = more filled bar (crisis shows full bar)
            const usagePercentage = Math.max(0, Math.min(100, ((24 - remainingHours) / 24) * 100));
            
            // Color based on crisis status
            let color = 'bg-green-500';
            if (crisisLikely) {
              color = 'bg-red-600';
            } else if (remainingHours < 6) {
              color = 'bg-orange-500';
            }
            
            return (
              <div key={pred?.facility_id || Math.random()} className="flex items-center gap-4">
                <div className="w-32 text-xs font-mono text-gray-300 truncate">
                  {pred?.facility_id || 'Unknown'}
                </div>
                <div className="flex-1 bg-slate-700 rounded-full overflow-hidden h-6">
                  <div
                    className={`${color} h-full transition-all duration-300 flex items-center justify-end pr-2`}
                    style={{ width: `${Math.max(usagePercentage, 5)}%` }}
                  >
                    {usagePercentage > 15 && (
                      <span className="text-xs font-bold text-white">
                        {remainingHours.toFixed(1)}h
                      </span>
                    )}
                  </div>
                </div>
                <div className="w-20 text-right text-xs">
                  {crisisLikely ? (
                    <span className="text-red-400 font-bold">⚠️ CRISIS</span>
                  ) : (
                    <span className="text-green-400">✓ Safe</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default BedPredictionPanel;
