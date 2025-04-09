import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet'; 
import MarkerClusterGroup from 'react-leaflet-markercluster'; 

import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

const greenIcon = new L.Icon({
  iconUrl: '/images/green_marker.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [0, -41]
});

const yellowIcon = new L.Icon({
  iconUrl: '/images/yellow_marker.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [0, -41]
});

const redIcon = new L.Icon({
  iconUrl: '/images/red_marker.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [0, -41]
});

const defaultIcon = greenIcon;

function App() {
  const [platforms, setPlatforms] = useState([]); 
  const [selectedPlatform, setSelectedPlatform] = useState(null); 
  const [isPanelVisible, setIsPanelVisible] = useState(true);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    // Загрузка данных платформ с сервера
    axios.get(`${backendUrl}/platforms`)
      .then((response) => {
        const platformsData = response.data.platforms.map((platform) => ({
          ...platform,
          image: `${backendUrl}/platform_photo/${platform.id}`, 
        }));
        setPlatforms(platformsData);
        console.log('Платформы:', platformsData); 
        setSelectedPlatform(null); 
      })
      .catch((error) => {
        console.error("Ошибка при загрузке данных:", error);
      });
  }, []);

  const loadDetails = async (id) => {
    try {
      // Загрузка подробной информации о платформе
      const response = await axios.get(`${backendUrl}/platform_info/${id}`, {
        params: { item_id: id } 
      });
      const platform = response.data;
      if (platform) {
        const imageResponse = await axios.get(`${backendUrl}/platform_photo/${id}`, { responseType: 'blob' });
        const imageUrl = URL.createObjectURL(imageResponse.data);
        const updatedPlatform = {
          ...platform,
          image: imageUrl,
        };
  
        setSelectedPlatform(updatedPlatform); 
        setIsPanelVisible(true); 
      } else {
        alert('Детали не найдены');
      }
    } catch (error) {
      console.error("Ошибка при загрузке деталей:", error);
      alert('Ошибка при загрузке деталей');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Боковая панель */}
      {isPanelVisible ? (
        <div
          className="side-panel"
          style={{
            width: '300px',
            backgroundColor: '#f9f9f9',
            borderRight: '1px solid #ddd',
            padding: '16px',
            boxSizing: 'border-box',
          }}
        >
          <button
            style={{
              position: 'absolute',
              top: '10px',
              left: '10px',
              zIndex: 1000,
              background: '#007bff',
              color: 'white',
              border: 'none',
              padding: '5px 10px',
              cursor: 'pointer',
              borderRadius: '5px',
            }}
            onClick={() => setIsPanelVisible(false)}
          >
            Свернуть
          </button>

          {selectedPlatform ? (
            <div>
              <h2>{selectedPlatform.address}</h2>
              <p><strong>Адрес:</strong> {selectedPlatform.address}</p>
              <p><strong>Координаты:</strong> ({selectedPlatform.latitude}, {selectedPlatform.longitude})</p>
              {/* Отображение изображения */}
              {selectedPlatform.image && (
                <img
                  src={selectedPlatform.image}
                  alt={selectedPlatform.address}
                  style={{ maxWidth: '100%', marginTop: '16px' }}
                />
              )}
            </div>
          ) : (
            <p>Выберите платформу на карте</p>
          )}
        </div>
      ) : (
        <button
          style={{
            position: 'absolute',
            top: '5%',
            left: '5%',
            zIndex: 1000,
            background: '#007bff',
            color: 'white',
            border: 'none',
            padding: '5px 10px',
            cursor: 'pointer',
            borderRadius: '5px',
          }}
          onClick={() => setIsPanelVisible(true)}
        >
          Развернуть
        </button>
      )}

      {/* Карта */}
      <div
        className="map-container"
        style={{
          flex: isPanelVisible ? '1' : '1 1 100%',
          height: '100%',
        }}
      >
        <MapContainer
          center={[55.148707, 61.433685]}
          zoom={12}
          style={{ width: '100%', height: '100%' }}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {/* Группировка маркеров */}
          <MarkerClusterGroup>
            {platforms.map((platform) => (
              <Marker
                key={platform.id}
                position={[platform.longitude, platform.latitude]}
                eventHandlers={{
                  click: () => loadDetails(platform.id),
                }}
                icon={getIconByFillLevel(platform.fill_level)} 
              />
            ))}
          </MarkerClusterGroup>
        </MapContainer>
      </div>
    </div>
  );
}

function getIconByFillLevel(fillLevel) {
  let fillLevelNumber;

  if (typeof fillLevel === 'string') {
    fillLevelNumber = parseFloat(fillLevel.replace('%', ''));
  } else {
    fillLevelNumber = fillLevel || 0; 
  }

  if (fillLevelNumber <= 30) {
    return greenIcon;
  } else if (fillLevelNumber <= 70) {
    return yellowIcon;
  } else {
    return redIcon;
  }
}

export default App;