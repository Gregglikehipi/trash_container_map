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
  const [containers, setContainers] = useState([]);
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [isPanelVisible, setIsPanelVisible] = useState(true); // Новое состояние для управления видимостью панели
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    // Загрузка координат мусорок
    axios.get(`${API_URL}/containers_coordinates.json`)
      .then((response) => {
        const coordinates = response.data.containers;

        // Загрузка деталей мусорок
        return axios.get(`${API_URL}/containers_details.json`).then((detailsResponse) => {
          const details = detailsResponse.data.containers;

          // Объединяем данные о координатах и деталях
          const enrichedContainers = coordinates.map((coord) => {
            const detail = details[coord.id];
            return {
              ...coord,
              fill_level: detail?.fill_level || "0%", // Добавляем fill_level из details
              name: detail?.name || "Неизвестное место", // Добавляем название для удобства
            };
          });

          setContainers(enrichedContainers);
        });
      })
      .catch((error) => {
        console.error("Ошибка при загрузке данных:", error);
      });
  }, []);

  const loadDetails = async (id) => {
    try {
      // Загрузка подробной информации о мусорке
      const response = await axios.get('http://localhost:8000/containers_details.json');
      const container = response.data.containers[id];
      if (container) {
        setSelectedContainer(container); // Устанавливаем выбранную мусорку
        setIsPanelVisible(true); // Автоматически разворачиваем панель
      } else {
        alert('Детали не найдены');
      }
    } catch (error) {
      alert('Ошибка при загрузке деталей');
    }
  };

  return (
    <div className="App"
    style={{ display: 'flex', height: '100%' }}>
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
              padding: '5px 5px',
              cursor: 'pointer',
              borderRadius: '5px',
            }}
            onClick={() => setIsPanelVisible(false)}
          >
            Свернуть
          </button>

          {selectedContainer ? (
            <div>
              <h2>{selectedContainer.name}</h2>
              <p><strong>Описание:</strong> {selectedContainer.description}</p>
              <p><strong>Заполненность:</strong> {selectedContainer.fill_level}</p>
              <p><strong>Оценка:</strong> {selectedContainer.rating} ⭐</p>
              {/* Отображение изображения */}
              {selectedContainer.image && (
                <img
                  src={selectedContainer.image}
                  alt={selectedContainer.name}
                  style={{ maxWidth: '100%', marginTop: '16px' }}
                />
              )}
            </div>
          ) : (
            <p>Выберите мусорку на карте</p>
          )}
        </div>
      ) : (
        <button
          style={{
            position: 'absolute',
            top: '5%',
            left: '3%',
            transform: 'translateY(-50%)',
            zIndex: 1000,
            background: '#007bff',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            cursor: 'pointer',
            borderRadius: '5px',
          }}
          onClick={() => setIsPanelVisible(true)}
        >
          Развернуть
        </button>
      )}

      {/* Карта */}
      <div style={{flex: 1, height: '100%'}}>
        <MapContainer center={[55.143029, 61.386887]} zoom={12} style={{ height: '100vh' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {/* Группировка маркеров */}
          <MarkerClusterGroup>
            {containers.map((container) => (
              <Marker
                key={container.id}
                position={[container.latitude, container.longitude]}
                eventHandlers={{
                  click: () => loadDetails(container.id),
                }}
                icon={getIconByFillLevel(container.fill_level)} // Определяем цвет по fill_level
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
    fillLevelNumber = fillLevel;
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