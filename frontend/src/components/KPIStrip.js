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
  const [downloading, setDownloading] = useState(false);

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

  /**
   * Download PDF report handler
   * Fetches the PDF from backend and triggers browser download
   */
  const handleDownloadReport = async () => {
    try {
      setDownloading(true);
      const response = await axios.get('http://localhost:8000/analytics/export-report', {
        responseType: 'blob', // Important: Handle response as binary
      });

      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `SMC_Health_Report_${new Date().toISOString().split('T')[0]}.pdf`
      );
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading report:', error);
      alert('Failed to download report. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-4">Loading KPIs...</div>;
  }

  return (
    <div className="space-y-4">
      {/* KPI Cards */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 p-6 rounded-lg">
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

      {/* Download Report Button */}
      <button
        onClick={handleDownloadReport}
        disabled={downloading}
        className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200 flex items-center justify-center gap-2 ${
          downloading
            ? 'bg-gray-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 active:scale-95'
        }`}
      >
        {downloading ? (
          <>
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating Report...
          </>
        ) : (
          <>
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            📄 Download Commissioner Report (PDF)
          </>
        )}
      </button>
    </div>
  );
};

export default KPIStrip;

