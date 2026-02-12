import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// ============================================================================
// TRANSLATIONS DICTIONARY
// ============================================================================
const translations = {
  en: {
    // Header
    headerTitle: 'Solapur Health Portal',
    tagline: 'Your Health, Our Priority',
    languageLabel: 'English',
    
    // Navigation
    tabVaccine: '💉 Vaccination Alerts',
    tabFacilities: '🏥 Nearby Facilities',
    tabWellness: '🏃 Wellness Programs',
    tabTelehealth: '📱 Telemedicine',
    
    // Vaccination Alerts
    vaccinationTitle: 'Upcoming Vaccination Drives',
    noVaccinations: 'No upcoming drives scheduled',
    driveType: 'Drive Type',
    location: 'Location',
    date: 'Date',
    time: 'Time',
    register: 'Register Now',
    
    // Facilities
    facilitiesTitle: 'Healthcare Facilities Near You',
    findNearest: '📍 Find Nearest Hospital',
    bedsAvailable: 'Beds Available',
    total: 'Total',
    occupied: 'Occupied',
    distance: 'Distance',
    callNow: 'Call Now',
    getDirections: 'Get Directions',
    hospitalStatus: 'Status',
    hospitalStatusGood: '✓ Good Availability',
    hospitalStatusWarning: '⚠️ Limited Availability',
    hospitalStatusCritical: '🚨 No Beds Available',
    
    // Wellness
    wellnessTitle: 'Community Health Programs',
    learnMore: 'Learn More',
    upcomingEvents: 'Upcoming Events',
    noEvents: 'No events scheduled',
    
    // Telemedicine
    telehealthTitle: 'Connect with Doctors',
    bookConsultation: 'Book Consultation',
    consultationTypes: 'Consultation Types',
    instantChat: 'Instant Chat Support',
    videoCall: '30-Minute Video Call',
    homeVisit: 'Doctor Home Visit',
    
    // Buttons
    yes: 'Yes',
    no: 'No',
    close: 'Close',
    back: 'Back',
    
    // Messages
    geolocationError: 'Unable to get your location. Please enable location services.',
    dataLoading: 'Loading...',
  },
  mr: {
    // Header
    headerTitle: 'सोलापूर आरोग्य पोर्टल',
    tagline: 'आपले आरोग्य, आमची प्राथमिकता',
    languageLabel: 'मराठी',
    
    // Navigation
    tabVaccine: '💉 लसीकरण सतर्कता',
    tabFacilities: '🏥 जवळील सुविधा',
    tabWellness: '🏃 आरोग्य कार्यक्रम',
    tabTelehealth: '📱 दूर चिकित्सा',
    
    // Vaccination Alerts
    vaccinationTitle: 'येणारे लसीकरण ड्राइव्ह',
    noVaccinations: 'कोणतेही साहित्य निर्धारित नाही',
    driveType: 'ड्राइव्ह प्रकार',
    location: 'स्थान',
    date: 'तारीख',
    time: 'वेळ',
    register: 'आता नोंदणी करा',
    
    // Facilities
    facilitiesTitle: 'आपल्या जवळ असलेल्या आरोग्य सुविधा',
    findNearest: '📍 जवळचे रुग्णालय शोधा',
    bedsAvailable: 'उपलब्ध बेड्स',
    total: 'एकूण',
    occupied: 'व्यस्त',
    distance: 'अंतर',
    callNow: 'आता कॉल करा',
    getDirections: 'दिशानिर्देश मिळवा',
    hospitalStatus: 'स्थिति',
    hospitalStatusGood: '✓ चांगली उपलब्धता',
    hospitalStatusWarning: '⚠️ मर्यादित उपलब्धता',
    hospitalStatusCritical: '🚨 कोणतेही बेड्स उपलब्ध नाहीत',
    
    // Wellness
    wellnessTitle: 'समुदाय आरोग्य कार्यक्रम',
    learnMore: 'अधिक जाणून घ्या',
    upcomingEvents: 'येणारे कार्यक्रम',
    noEvents: 'कोणतेही कार्यक्रम निर्धारित नाही',
    
    // Telemedicine
    telehealthTitle: 'डॉक्टरांशी जोडा',
    bookConsultation: 'परामर्श बुक करा',
    consultationTypes: 'परामर्श प्रकार',
    instantChat: 'तत्काल चॅट समर्थन',
    videoCall: '३० मिनिटाचा व्हिडिओ कॉल',
    homeVisit: 'डॉक्टर होम व्हिজिट',
    
    // Buttons
    yes: 'होय',
    no: 'नाही',
    close: 'बंद करा',
    back: 'मागे',
    
    // Messages
    geolocationError: 'आपल्या स्थानावर पहुंच मिळू शकली नाही. कृपया स्थान सेवा सक्षम करा.',
    dataLoading: 'लोड होत आहे...',
  }
};

// ============================================================================
// MOCK DATA
// ============================================================================
const mockVaccinationDrives = [
  { id: 1, type: 'Polio Drive', location: 'Ward-5 Community Center', date: 'Feb 15', time: '10:00 AM - 2:00 PM', target: '500 children' },
  { id: 2, type: 'COVID-19 Booster', location: 'Civil Hospital', date: 'Feb 16', time: '9:00 AM - 5:00 PM', target: 'All adults' },
  { id: 3, type: 'Hepatitis B', location: 'Ward-2 PHC', date: 'Feb 18', time: '11:00 AM - 3:00 PM', target: 'Infants & children' },
];

const mockHealthFacilities = [
  {
    id: 1,
    name: 'Civil Hospital Solapur',
    type: 'Hospital',
    beds: { total: 150, occupied: 98, available: 52 },
    phone: '+91-217-2626262',
    lat: 17.6578,
    lng: 75.9244,
    distance: 1.2,
  },
  {
    id: 2,
    name: 'Ward-5 PHC',
    type: 'PHC',
    beds: { total: 25, occupied: 18, available: 7 },
    phone: '+91-217-2626263',
    lat: 17.6480,
    lng: 75.9350,
    distance: 0.8,
  },
  {
    id: 3,
    name: 'Diagnostic Lab - Central',
    type: 'Lab',
    beds: { total: 0, occupied: 0, available: 0 },
    phone: '+91-217-2626264',
    lat: 17.6620,
    lng: 75.9180,
    distance: 1.5,
  },
  {
    id: 4,
    name: 'Private Hospital Pandharpur',
    type: 'Hospital',
    beds: { total: 100, occupied: 65, available: 35 },
    phone: '+91-217-2626265',
    lat: 17.6300,
    lng: 75.9100,
    distance: 2.3,
  },
];

const mockWellnessPrograms = [
  {
    id: 1,
    title: 'Yoga in the Park',
    description: 'Strengthen your body and mind with guided yoga sessions every morning in beautiful natural surroundings.',
    schedule: 'Mon-Wed-Fri, 6:00 AM',
    location: 'Solapur Central Park',
    icon: '🧘',
  },
  {
    id: 2,
    title: 'Dengue Prevention Tips',
    description: 'Learn essential prevention techniques and awareness about dengue transmission and protection.',
    schedule: 'Saturday workshops',
    location: 'Community Centers',
    icon: '🦟',
  },
  {
    id: 3,
    title: 'Cancer Screening Camp',
    description: 'Free health screening and consultation with expert doctors. Early detection saves lives.',
    schedule: 'Monthly (2nd Saturday)',
    location: 'Civil Hospital',
    icon: '🏥',
  },
  {
    id: 4,
    title: 'Mental Health Support',
    description: 'Counseling and support groups for mental wellbeing. Your mental health matters.',
    schedule: 'Weekly sessions',
    location: 'Health Department',
    icon: '🧠',
  },
];

// ============================================================================
// CITIZEN DASHBOARD COMPONENT
// ============================================================================
const CitizenHealthPortal = ({ onToggleView, language, onLanguageChange }) => {
  const t = translations[language];
  const [activeTab, setActiveTab] = useState('vaccine');
  const [map, setMap] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [facilities, setFacilities] = useState(mockHealthFacilities);
  const [selectedFacility, setSelectedFacility] = useState(null);

  useEffect(() => {
    // Request geolocation (default to Solapur center if denied)
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation([position.coords.latitude, position.coords.longitude]);
        },
        () => {
          // Default to Solapur center: 17.6578, 75.9244
          setUserLocation([17.6578, 75.9244]);
        }
      );
    } else {
      setUserLocation([17.6578, 75.9244]);
    }
  }, []);

  const handleFindNearest = () => {
    if (userLocation) {
      const nearest = facilities.reduce((prev, current) => {
        const distance = Math.sqrt(
          Math.pow(current.lat - userLocation[0], 2) +
          Math.pow(current.lng - userLocation[1], 2)
        );
        return distance < prev.distance ? { ...current, distance } : prev;
      });
      setSelectedFacility(nearest);
      setActiveTab('facilities');
    }
  };

  const getBedStatusColor = (facility) => {
    if (facility.beds.total === 0) return 'from-blue-400 to-blue-600';
    const occupancyRate = facility.beds.occupied / facility.beds.total;
    if (occupancyRate < 0.5) return 'from-green-400 to-green-600';
    if (occupancyRate < 0.9) return 'from-yellow-400 to-yellow-600';
    return 'from-red-400 to-red-600';
  };

  const getBedStatusIcon = (facility) => {
    if (facility.beds.total === 0) return t.hospitalStatus;
    const occupancyRate = facility.beds.occupied / facility.beds.total;
    if (occupancyRate < 0.5) return t.hospitalStatusGood;
    if (occupancyRate < 0.9) return t.hospitalStatusWarning;
    return t.hospitalStatusCritical;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white shadow-md border-b-4 border-emerald-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="text-4xl">🏥</div>
            <div>
              <h1 className="text-2xl font-bold text-emerald-700">{t.headerTitle}</h1>
              <p className="text-sm text-gray-600">{t.tagline}</p>
            </div>
          </div>

          {/* Language Toggle */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => onLanguageChange('en')}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                language === 'en'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              English
            </button>
            <button
              onClick={() => onLanguageChange('mr')}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                language === 'mr'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              मराठी
            </button>
            <button
              onClick={onToggleView}
              className="ml-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold text-sm transition"
            >
              🔄 Admin View
            </button>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-300 sticky top-20 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-4 overflow-x-auto py-3">
            {[
              { id: 'vaccine', label: t.tabVaccine },
              { id: 'facilities', label: t.tabFacilities },
              { id: 'wellness', label: t.tabWellness },
              { id: 'telehealth', label: t.tabTelehealth },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-semibold whitespace-nowrap transition ${
                  activeTab === tab.id
                    ? 'bg-emerald-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ===== VACCINATION ALERTS TAB ===== */}
        {activeTab === 'vaccine' && (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-800 text-center">{t.vaccinationTitle}</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockVaccinationDrives.length > 0 ? (
                mockVaccinationDrives.map((drive) => (
                  <div key={drive.id} className="bg-white rounded-lg shadow-lg border-l-4 border-emerald-600 hover:shadow-xl transition transform hover:scale-105">
                    <div className="p-6">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-bold text-gray-800">{drive.type}</h3>
                        <span className="text-2xl">💉</span>
                      </div>
                      <div className="space-y-2 text-sm text-gray-600 mb-4">
                        <p><span className="font-semibold">📍 {t.location}:</span> {drive.location}</p>
                        <p><span className="font-semibold">📅 {t.date}:</span> {drive.date}</p>
                        <p><span className="font-semibold">🕐 {t.time}:</span> {drive.time}</p>
                        <p><span className="font-semibold">👥 Target:</span> {drive.target}</p>
                      </div>
                      <button className="w-full bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 font-semibold transition">
                        {t.register}
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-12 text-gray-500">{t.noVaccinations}</div>
              )}
            </div>
          </div>
        )}

        {/* ===== FACILITIES TAB ===== */}
        {activeTab === 'facilities' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-3xl font-bold text-gray-800">{t.facilitiesTitle}</h2>
              <button
                onClick={handleFindNearest}
                className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-semibold transition shadow-lg"
              >
                {t.findNearest}
              </button>
            </div>

            {/* Map */}
            {userLocation && (
              <div className="rounded-lg overflow-hidden shadow-lg h-96 border-2 border-emerald-300">
                <MapContainer center={userLocation} zoom={14} style={{ height: '100%', width: '100%' }}>
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; OpenStreetMap contributors'
                  />
                  {/* User Location */}
                  <CircleMarker center={userLocation} radius={10} fillColor="blue" color="blue" weight={2} opacity={0.8} fillOpacity={0.8}>
                    <Popup>Your Location</Popup>
                  </CircleMarker>

                  {/* Facilities */}
                  {facilities.map((facility) => (
                    <Marker
                      key={facility.id}
                      position={[facility.lat, facility.lng]}
                      icon={L.icon({
                        iconUrl: facility.type === 'Hospital' ? '🏥' : '⚕️',
                        iconSize: [32, 32],
                      })}
                    >
                      <Popup>
                        <div className="text-sm">
                          <strong>{facility.name}</strong>
                          <p>Beds: {facility.beds.available}/{facility.beds.total}</p>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            )}

            {/* Facility Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
              {facilities.map((facility) => (
                <div
                  key={facility.id}
                  className={`bg-gradient-to-br ${getBedStatusColor(facility)} rounded-lg shadow-lg text-white p-6 hover:shadow-xl transition transform hover:scale-105 cursor-pointer`}
                  onClick={() => setSelectedFacility(facility)}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold">{facility.name}</h3>
                      <p className="text-sm opacity-90">{facility.type}</p>
                    </div>
                    <span className="text-3xl">{facility.type === 'Hospital' ? '🏥' : '⚕️'}</span>
                  </div>

                  {facility.beds.total > 0 && (
                    <div className="mb-4 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>{t.bedsAvailable}:</span>
                        <span className="font-bold">{facility.beds.available}/{facility.beds.total}</span>
                      </div>
                      <div className="w-full bg-white bg-opacity-30 rounded-full h-2">
                        <div
                          className="bg-white h-2 rounded-full"
                          style={{ width: `${(facility.beds.available / facility.beds.total) * 100}%` }}
                        ></div>
                      </div>
                      <p className="text-xs opacity-80">{t.hospitalStatusGood}</p>
                    </div>
                  )}

                  <div className="flex gap-2 text-sm">
                    <button className="flex-1 bg-white text-gray-800 py-2 rounded font-semibold hover:bg-gray-100 transition">
                      {t.callNow}
                    </button>
                    <button className="flex-1 bg-white bg-opacity-20 py-2 rounded font-semibold hover:bg-opacity-30 transition">
                      {t.getDirections}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ===== WELLNESS PROGRAMS TAB ===== */}
        {activeTab === 'wellness' && (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-800 text-center">{t.wellnessTitle}</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
              {mockWellnessPrograms.map((program) => (
                <div key={program.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition transform hover:scale-105">
                  <div className="bg-gradient-to-r from-emerald-400 to-teal-400 p-6 text-white">
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-xl font-bold">{program.title}</h3>
                      <span className="text-4xl">{program.icon}</span>
                    </div>
                    <p className="text-sm opacity-90">{program.description}</p>
                  </div>
                  <div className="p-6 space-y-3">
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold">📅 Schedule:</span> {program.schedule}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold">📍 Location:</span> {program.location}
                    </p>
                    <button className="w-full bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 font-semibold transition">
                      {t.learnMore}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ===== TELEMEDICINE TAB ===== */}
        {activeTab === 'telehealth' && (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-800 text-center">{t.telehealthTitle}</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { icon: '💬', title: t.instantChat, description: 'Real-time chat support with healthcare professionals' },
                { icon: '📹', title: t.videoCall, description: 'Direct video consultation with licensed doctors' },
                { icon: '🚗', title: t.homeVisit, description: 'Doctor visits your home for examination' },
              ].map((service, idx) => (
                <div key={idx} className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition transform hover:scale-105">
                  <div className="text-5xl mb-4 text-center">{service.icon}</div>
                  <h3 className="text-lg font-bold text-gray-800 text-center mb-2">{service.title}</h3>
                  <p className="text-sm text-gray-600 text-center mb-4">{service.description}</p>
                  <button className="w-full bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 font-semibold transition">
                    {t.bookConsultation}
                  </button>
                </div>
              ))}
            </div>

            {/* Emergency Contact */}
            <div className="bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg p-8 text-center">
              <h3 className="text-2xl font-bold mb-2">🚨 {language === 'en' ? 'Emergency?' : 'आपातकाल?'}</h3>
              <p className="text-lg mb-4">{language === 'en' ? 'Call 108 for immediate medical assistance' : 'तात्काळ चिकित्सा सहायतासाठी 108 वर कॉल करा'}</p>
              <button className="bg-white text-red-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition text-lg">
                {language === 'en' ? 'Call Emergency Services' : 'आपातकालीन सेवा कॉल करा'}
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-400">
          <p>© 2026 Solapur Municipal Corporation (SMC) | {language === 'en' ? 'Your Health Portal' : 'आपले आरोग्य पोर्टल'}</p>
        </div>
      </footer>
    </div>
  );
};

export default CitizenHealthPortal;
