import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  MapContainer,
  TileLayer,
  GeoJSON as GeoJSONComponent,
  Popup,
} from 'react-leaflet';
import L from 'leaflet';

const WardHeatmap = () => {
  const [geoJsonData, setGeoJsonData] = useState(null);
  const [wardData, setWardData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Solapur city center
  const SOLAPUR_CENTER = [17.6599, 75.9064];

  useEffect(() => {
    const fetchWardData = async () => {
      try {
        const res = await axios.get('http://localhost:8000/analytics/ward-risk');
        const wards = res.data.wards || [];
        setWardData(wards);

        // Create GeoJSON from ward data
        // In a real scenario, you'd fetch this from a GeoJSON file or API
        const features = wards.map((ward, idx) => ({
          type: 'Feature',
          properties: {
            ward_name: ward.ward,
            risk_level: ward.risk_level,
            risk_score: ward.risk_score,
            icu_pressure: ward.icu_pressure,
            recent_cases: ward.recent_cases,
          },
          geometry: {
            type: 'Point',
            // Distribute wards in a circle around Solapur center for demo
            coordinates: [
              SOLAPUR_CENTER[1] + (Math.random() - 0.5) * 0.2,
              SOLAPUR_CENTER[0] + (Math.random() - 0.5) * 0.2,
            ],
          },
        }));

        setGeoJsonData({
          type: 'FeatureCollection',
          features: features,
        });
      } catch (error) {
        console.error('Error fetching ward data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWardData();
  }, []);

  /**
   * Get color based on risk level
   * 0-25 (Green), 25-50 (Yellow), 50-75 (Orange), 75+ (Red)
   */
  const getRiskColor = (riskScore) => {
    if (riskScore >= 75) return '#dc2626'; // Red
    if (riskScore >= 50) return '#ea580c'; // Orange
    if (riskScore >= 25) return '#eab308'; // Yellow
    return '#22c55e'; // Green
  };

  /**
   * Get risk level from score
   */
  const getRiskLevel = (riskScore) => {
    if (riskScore >= 75) return 'CRITICAL';
    if (riskScore >= 50) return 'HIGH';
    if (riskScore >= 25) return 'MEDIUM';
    return 'LOW';
  };

  /**
   * Style function for GeoJSON features
   */
  const onEachFeature = (feature, layer) => {
    const props = feature.properties;
    const riskScore = props.risk_score || 0;
    const color = getRiskColor(riskScore);

    // Style the marker
    const markerIcon = L.divIcon({
      className: 'risk-marker',
      html: `
        <div style="
          background-color: ${color};
          border: 3px solid white;
          border-radius: 50%;
          width: 35px;
          height: 35px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 12px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        ">
          ${riskScore.toFixed(0)}
        </div>
      `,
      iconSize: [35, 35],
      iconAnchor: [17, 17],
    });

    if (layer.setIcon) {
      layer.setIcon(markerIcon);
    }

    // Create popup content
    const popupContent = `
      <div style="font-family: Arial, sans-serif; min-width: 200px;">
        <h3 style="margin: 0 0 8px 0; color: #333; font-size: 14px;">
          ${props.ward_name}
        </h3>
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 4px 0; color: #666; font-size: 12px;">Risk Level:</td>
            <td style="padding: 4px 0; color: #333; font-weight: bold; font-size: 12px;">
              <span style="
                background-color: ${color};
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                display: inline-block;
              ">
                ${getRiskLevel(riskScore)}
              </span>
            </td>
          </tr>
          <tr>
            <td style="padding: 4px 0; color: #666; font-size: 12px;">Risk Score:</td>
            <td style="padding: 4px 0; color: #333; font-weight: bold; font-size: 12px;">
              ${riskScore.toFixed(1)} / 100
            </td>
          </tr>
          <tr>
            <td style="padding: 4px 0; color: #666; font-size: 12px;">ICU Pressure:</td>
            <td style="padding: 4px 0; color: #333; font-weight: bold; font-size: 12px;">
              ${(props.icu_pressure || 0).toFixed(1)}%
            </td>
          </tr>
          <tr>
            <td style="padding: 4px 0; color: #666; font-size: 12px;">Recent Cases:</td>
            <td style="padding: 4px 0; color: #333; font-weight: bold; font-size: 12px;">
              ${props.recent_cases || 0}
            </td>
          </tr>
        </table>
      </div>
    `;

    layer.bindPopup(popupContent);
  };

  if (loading) {
    return <div className="flex justify-center items-center p-6 bg-slate-800 rounded-lg h-96">
      <p className="text-gray-300">Loading GIS map...</p>
    </div>;
  }

  return (
    <div className="bg-slate-800 p-6 rounded-lg mb-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">🗺️ Ward Risk GIS Heatmap</h2>

      {/* Map Container */}
      <div className="rounded-lg overflow-hidden mb-4" style={{ height: '500px' }}>
        {geoJsonData && (
          <MapContainer
            center={SOLAPUR_CENTER}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
          >
            {/* OpenStreetMap Tile Layer */}
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />

            {/* GeoJSON Layer with Risk Markers */}
            <GeoJSONComponent
              data={geoJsonData}
              onEachFeature={onEachFeature}
            />
          </MapContainer>
        )}
      </div>

      {/* Risk Distribution Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
        <div className="bg-slate-700 p-3 rounded border-l-4 border-green-500">
          <p className="text-xs text-gray-400">LOW</p>
          <p className="text-2xl font-bold text-green-400">
            {wardData.filter((w) => w.risk_score < 25).length}
          </p>
        </div>
        <div className="bg-slate-700 p-3 rounded border-l-4 border-yellow-500">
          <p className="text-xs text-gray-400">MEDIUM</p>
          <p className="text-2xl font-bold text-yellow-400">
            {wardData.filter((w) => w.risk_score >= 25 && w.risk_score < 50).length}
          </p>
        </div>
        <div className="bg-slate-700 p-3 rounded border-l-4 border-orange-500">
          <p className="text-xs text-gray-400">HIGH</p>
          <p className="text-2xl font-bold text-orange-400">
            {wardData.filter((w) => w.risk_score >= 50 && w.risk_score < 75).length}
          </p>
        </div>
        <div className="bg-slate-700 p-3 rounded border-l-4 border-red-600">
          <p className="text-xs text-gray-400">CRITICAL</p>
          <p className="text-2xl font-bold text-red-400">
            {wardData.filter((w) => w.risk_score >= 75).length}
          </p>
        </div>
        <div className="bg-slate-700 p-3 rounded border-l-4 border-blue-500">
          <p className="text-xs text-gray-400">Total Wards</p>
          <p className="text-2xl font-bold text-blue-400">{wardData.length}</p>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-slate-700 p-4 rounded border border-slate-600">
        <h3 className="text-sm font-bold text-white mb-3">📊 Legend</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center gap-2">
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '50%',
                backgroundColor: '#22c55e',
                border: '3px solid white',
              }}
            />
            <span className="text-xs text-gray-300">Green: 0-25 (LOW)</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '50%',
                backgroundColor: '#eab308',
                border: '3px solid white',
              }}
            />
            <span className="text-xs text-gray-300">Yellow: 25-50 (MEDIUM)</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '50%',
                backgroundColor: '#ea580c',
                border: '3px solid white',
              }}
            />
            <span className="text-xs text-gray-300">Orange: 50-75 (HIGH)</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '50%',
                backgroundColor: '#dc2626',
                border: '3px solid white',
              }}
            />
            <span className="text-xs text-gray-300">Red: 75+ (CRITICAL)</span>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-4 bg-blue-900 border border-blue-700 rounded p-3">
        <p className="text-xs text-blue-200">
          <strong>ℹ️ Info:</strong> Click on each marker to view ward details including ICU pressure and recent cases.
          Map is centered on Solapur (17.6599° N, 75.9064° E).
        </p>
      </div>
    </div>
  );
};

export default WardHeatmap;

