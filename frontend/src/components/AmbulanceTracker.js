import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AmbulanceTracker = () => {
  const [ambulances, setAmbulances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fleetStatus, setFleetStatus] = useState(null);
  const [showNearestModal, setShowNearestModal] = useState(false);
  const [nearestResults, setNearestResults] = useState([]);
  const [searchLat, setSearchLat] = useState(19.861);
  const [searchLng, setSearchLng] = useState(75.3272);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    const fetchFleetStatus = async () => {
      try {
        const statusRes = await axios.get('http://localhost:8000/ambulances/status');
        setFleetStatus(statusRes.data);
      } catch (error) {
        console.error('Error fetching fleet status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFleetStatus();
  }, []);

  const handleFindNearest = async () => {
    setSearching(true);
    try {
      const res = await axios.get('http://localhost:8000/ambulances/nearest', {
        params: {
          lat: searchLat,
          lng: searchLng,
          limit: 5,
          available_only: true,
        },
      });
      setNearestResults(res.data.ambulances || []);
    } catch (error) {
      console.error('Error finding nearest:', error);
    } finally {
      setSearching(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-4">Loading ambulances...</div>;
  }

  return (
    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">🚑 Ambulance Tracker</h2>

      {/* Fleet Status */}
      {fleetStatus && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-700 p-3 rounded text-center">
            <p className="text-xs text-gray-400">Total</p>
            <p className="text-2xl font-bold text-white">{fleetStatus.total_ambulances}</p>
          </div>
          <div className="bg-green-900 p-3 rounded text-center">
            <p className="text-xs text-gray-400">Available</p>
            <p className="text-2xl font-bold text-green-400">
              {fleetStatus.status_breakdown?.AVAILABLE || 0}
            </p>
          </div>
          <div className="bg-yellow-900 p-3 rounded text-center">
            <p className="text-xs text-gray-400">Busy</p>
            <p className="text-2xl font-bold text-yellow-400">
              {fleetStatus.status_breakdown?.BUSY || 0}
            </p>
          </div>
          <div className="bg-gray-700 p-3 rounded text-center">
            <p className="text-xs text-gray-400">Offline</p>
            <p className="text-2xl font-bold text-gray-400">
              {fleetStatus.status_breakdown?.OFFLINE || 0}
            </p>
          </div>
        </div>
      )}

      {/* Find Nearest Button */}
      <button
        onClick={() => setShowNearestModal(true)}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg mb-6 transition-colors"
      >
        👉 Find Nearest Ambulance
      </button>

      {/* Nearest Ambulance Modal */}
      {showNearestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-600 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold text-white mb-4">Find Nearest Ambulance</h3>

            {/* Coordinate Input */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="text-sm text-gray-300">Latitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={searchLat}
                  onChange={(e) => setSearchLat(parseFloat(e.target.value))}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded mt-1"
                  placeholder="19.861"
                />
              </div>
              <div>
                <label className="text-sm text-gray-300">Longitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={searchLng}
                  onChange={(e) => setSearchLng(parseFloat(e.target.value))}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded mt-1"
                  placeholder="75.3272"
                />
              </div>
            </div>

            {/* Search Button */}
            <button
              onClick={handleFindNearest}
              disabled={searching}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg mb-4 disabled:opacity-50"
            >
              {searching ? 'Searching...' : 'Search'}
            </button>

            {/* Results */}
            {nearestResults.length > 0 && (
              <div className="space-y-3 mb-6 max-h-64 overflow-y-auto">
                {nearestResults.map((amb, idx) => (
                  <div key={idx} className="bg-slate-700 p-3 rounded">
                    <p className="font-mono text-sm font-bold text-white">{amb.vehicle_id}</p>
                    <div className="text-xs text-gray-300 mt-1 space-y-1">
                      <p>Ward: {amb.ward}</p>
                      <p>Status: <span className={amb.status === 'AVAILABLE' ? 'text-green-400' : 'text-yellow-400'}>{amb.status}</span></p>
                      <p>Distance: <span className="text-blue-400 font-bold">{amb.distance_km} km</span></p>
                      <p className="text-gray-500">Coords: {amb.lat.toFixed(4)}, {amb.lng.toFixed(4)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {nearestResults.length === 0 && !searching && (
              <p className="text-gray-400 text-sm mb-6">Click Search to find nearest ambulances</p>
            )}

            {/* Close Button */}
            <button
              onClick={() => {
                setShowNearestModal(false);
                setNearestResults([]);
              }}
              className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-2 px-4 rounded-lg"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AmbulanceTracker;
