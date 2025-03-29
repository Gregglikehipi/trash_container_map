import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet'; // Импортируем Leaflet

// Импортируем CSS Leaflet для использования стандартных стилей и иконок
import 'leaflet/dist/leaflet.css';

// Переопределение пути к иконкам (если они не загружаются)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'), // Путь к retina-иконке
  iconUrl: require('leaflet/dist/images/marker-icon.png'),         // Путь к обычной иконке
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),    // Путь к тени иконки
});

function App() {
  const [containers, setContainers] = useState([]);
  const [selectedContainer, setSelectedContainer] = useState(null);

  useEffect(() => {
    // Загрузка координат мусорок
    axios.get('http://localhost:8000/containers_coordinates.json')
      .then((response) => {
        setContainers(response.data.containers);
      });
  }, []);

  const loadDetails = async (id) => {
    try {
      // Загрузка подробной информации о мусорке
      const response = await axios.get('http://localhost:8000/containers_details.json');
      const container = response.data.containers[id];
      if (container) {
        setSelectedContainer(container); // Устанавливаем выбранную мусорку
      } else {
        alert('Детали не найдены');
      }
    } catch (error) {
      alert('Ошибка при загрузке деталей');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Панель с информацией */}
      <div
        style={{
          width: '300px',
          backgroundColor: '#f9f9f9',
          borderRight: '1px solid #ddd',
          padding: '16px',
          boxSizing: 'border-box',
        }}
      >
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

      {/* Карта */}
      <div style={{ flex: 1 }}>
        <MapContainer center={[55.143029, 61.386887]} zoom={12} style={{ height: '100%' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {containers.map((container) => (
            <Marker
              key={container.id}
              position={[container.latitude, container.longitude]}
              eventHandlers={{
                click: () => loadDetails(container.id),
              }}
            />
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

export default App;