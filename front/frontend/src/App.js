import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet'; // Импортируем Leaflet
import MarkerClusterGroup from 'react-leaflet-markercluster'; // Добавляем импорт

// Импортируем CSS Leaflet для использования стандартных стилей и иконок
import 'leaflet/dist/leaflet.css';

import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

// Создаем кастомные иконки для разных уровней заполненности
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

function App() {
  const [platforms, setPlatforms] = useState([]); // Состояние для хранения платформ
  const [selectedPlatform, setSelectedPlatform] = useState(null); // Выбранная платформа
  const [isPanelVisible, setIsPanelVisible] = useState(true); // Состояние видимости боковой панели

  useEffect(() => {
    // Загрузка данных платформ с сервера
    axios.get('http://python-app:8000/platforms.json') // Используем python-app внутри Docker
      .then((response) => {
        const platformsData = response.data.platforms.map((platform) => ({
          ...platform,
          image: `/platform_photo/${platform.id}`, // Добавляем путь к изображению
        }));
        setPlatforms(platformsData);
        setSelectedPlatform(null); // Сбрасываем выбранную платформу
      })
      .catch((error) => {
        console.error("Ошибка при загрузке данных:", error);
      });
  }, []);

  const loadDetails = async (id) => {
    try {
      // Загрузка подробной информации о платформе
      const response = await axios.get(`http://python-app:8000/platforms/${id}`); // Используем python-app внутри Docker
      const platform = response.data;
      if (platform) {
        setSelectedPlatform(platform); // Устанавливаем выбранную платформу
        setIsPanelVisible(true); // Автоматически разворачиваем панель
      } else {
        alert('Детали не найдены');
      }
    } catch (error) {
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
            left: '3%',
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
          center={[55.143029, 61.386887]}
          zoom={12}
          style={{ width: '100%', height: '100%' }}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {/* Группировка маркеров */}
          <MarkerClusterGroup>
            {platforms.map((platform) => (
              <Marker
                key={platform.id}
                position={[platform.latitude, platform.longitude]}
                eventHandlers={{
                  click: () => loadDetails(platform.id),
                }}
                icon={getIconByFillLevel(platform.fill_level)} // Определяем цвет по fill_level
              />
            ))}
          </MarkerClusterGroup>
        </MapContainer>
      </div>
    </div>
  );
}

// Функция для выбора иконки по заполненности
function getIconByFillLevel(fillLevel) {
  let fillLevelNumber;

  // Если fillLevel — строка, убираем символ '%'
  if (typeof fillLevel === 'string') {
    fillLevelNumber = parseFloat(fillLevel.replace('%', ''));
  } else {
    // Если fillLevel уже число
    fillLevelNumber = fillLevel || 0; // По умолчанию 0%, если данные отсутствуют
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