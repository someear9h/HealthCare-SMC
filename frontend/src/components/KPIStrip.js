import React, { useState, useEffect } from 'react';
import axios from 'axios';

const KPIStrip = () => {
  const [kpis, setKpis] = useState({
    totalBeds: 0,
    totalIcu: 0,
    crisisFacilities: 0,
    highRiskWards: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        // Fetch city totals and predictions/wards
        const totalsRes = await axios.get('http://localhost:8000/analytics/city-totals');
        const predRes = await axios.get('http://localhost:8000/analytics/predicted-capacity');
        const wardsRes = await axios.get('http://localhost:8000/analytics/ward-risk');

        const predictions = predRes.data.predictions || [];
        const crisisCount = predictions.filter((p) => p.crisis_likely).length;
        const wards = wardsRes.data.wards || [];
        const highRiskCount = wards.filter((w) => w.risk_level === 'HIGH' || w.risk_level === 'CRITICAL').length;

        setKpis({
          totalBeds: totalsRes.data.city_totals?.total_beds || 0,
          totalIcu: totalsRes.data.city_totals?.total_icu || 0,
          crisisFacilities: crisisCount,
          highRiskWards: highRiskCount,
        });
      } catch (error) {
        console.error('Error fetching KPIs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchKPIs();
    const interval = setInterval(fetchKPIs, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="flex justify-center p-4">Loading KPIs...</div>;
  }

  return (
    <div className="bg-gradient-to-r from-slate-900 to-slate-800 p-6 rounded-lg mb-6">
      <div className="grid grid-cols-4 gap-4">
        {/* Total Beds */}
        <div className="bg-slate-700 p-4 rounded-lg border-l-4 border-blue-500">
          <p className="text-sm text-gray-300">Total Beds Available</p>
          <p className="text-3xl font-bold text-blue-400">{kpis.totalBeds}</p>
        </div>

        {/* ICU */}
        <div className="bg-slate-700 p-4 rounded-lg border-l-4 border-purple-500">
          <p className="text-sm text-gray-300">ICU Available</p>
          <p className="text-3xl font-bold text-purple-400">{kpis.totalIcu}</p>
        </div>

        {/* Crisis Facilities */}
        <div className={`p-4 rounded-lg border-l-4 ${kpis.crisisFacilities > 0 ? 'bg-red-900 border-red-500' : 'bg-slate-700 border-green-500'}`}>
          <p className="text-sm text-gray-300">Crisis Facilities</p>
          <p className={`text-3xl font-bold ${kpis.crisisFacilities > 0 ? 'text-red-400' : 'text-green-400'}`}>
            {kpis.crisisFacilities}
          </p>
        </div>

        {/* High Risk Wards */}
        <div className={`p-4 rounded-lg border-l-4 ${kpis.highRiskWards > 0 ? 'bg-orange-900 border-orange-500' : 'bg-slate-700 border-green-500'}`}>
          <p className="text-sm text-gray-300">High Risk Wards</p>
          <p className={`text-3xl font-bold ${kpis.highRiskWards > 0 ? 'text-orange-400' : 'text-green-400'}`}>
            {kpis.highRiskWards}
          </p>
        </div>
      </div>
    </div>
  );
};

export default KPIStrip;
