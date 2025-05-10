import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet'; 
import MarkerClusterGroup from 'react-leaflet-markercluster'; 

import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

// Определение иконок
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
  const [platforms, setPlatforms] = useState([]); 
  const [selectedPlatform, setSelectedPlatform] = useState(null); 
  const [isPanelVisible, setIsPanelVisible] = useState(true);
  const [comments, setComments] = useState([]); // Новое состояние для комментариев
  const [commentText, setCommentText] = useState(''); // Новое состояние для текста комментария

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    // Загрузка данных платформ с сервера
    axios.get(`${backendUrl}/platforms`)
      .then((response) => {
        const platformsData = response.data.platforms.map((platform) => ({
          ...platform,
          image: `${backendUrl}/platform_photo/${formatId(platform.id)}`, 
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
      const formattedId = formatId(id); // форматируем ID
  
      // Загружаем основную информацию о платформе
      const response = await axios.get(`${backendUrl}/platform_info/${formattedId}`, {
        params: { item_id: formattedId }
      });
  
      const platform = response.data;
  
      if (platform) {
        let imageUrl = null;
  
        // Пытаемся загрузить фото, но не падаем, если его нет
        try {
          const imageResponse = await axios.get(`${backendUrl}/platform_photo/${formattedId}`, {
            responseType: 'blob'
          });
          imageUrl = URL.createObjectURL(imageResponse.data);
        } catch (imageError) {
          console.warn("Фото не найдено:", imageError);
          // Если фото не найдено — просто продолжаем без него
        }
  
        // Получаем комментарии
        const commentsResponse = await axios.get(`${backendUrl}/comments/${formattedId}`);
        const commentsData = commentsResponse.data;
  
        // Устанавливаем данные платформы (с фото или без)
        setSelectedPlatform({
          ...platform,
          id: formattedId,
          image: imageUrl, // может быть null
        });
  
        setComments(commentsData);
        setIsPanelVisible(true);
      } else {
        alert('Детали не найдены');
      }
    } catch (error) {
      console.error("Ошибка при загрузке деталей:", error);
      alert('Ошибка при загрузке деталей');
    }
  };

const handleSubmitComment = async (event) => {
  event.preventDefault();

  if (!selectedPlatform) {
    alert('Выберите платформу для добавления комментария');
    return;
  }

  try {
    const response = await axios.post(
      `${backendUrl}/comments/${selectedPlatform.id}`, // Используем правильный эндпоинт
      { text: commentText } // Отправляем текст в теле запроса
    );

    setComments([...comments, response.data]); // Добавляем новый комментарий к списку
    setCommentText(''); // Очищаем поле ввода

    console.log('Комментарий успешно добавлен:', response.data);
  } catch (error) {
    console.error("Ошибка при отправке комментария:", error);
    alert('Ошибка при отправке комментария');
  }
};

  const formatId = (id) => {
    return String(id).padStart(8, '0'); // делаем строкой и дополняем до 8 знаков нулями слева
  };

  const getIconByStatus = (status) => {
    switch (status) {
      case 'green':
        return greenIcon;
      case 'yellow':
        return yellowIcon;
      case 'red':
        return redIcon;
      default:
        return greenIcon;
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
              {/* Форма для отправки комментария */}
              <div style={{ marginTop: '20px' }}>
                <h3>Добавить комментарий</h3>
                <form onSubmit={handleSubmitComment}>
                  <input
                    type="text"
                    placeholder="Введите ваш комментарий..."
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    required
                  />
                  <button type="submit">Отправить</button>
                </form>
              </div>
              {/* Отображение существующих комментариев */}
              <div style={{ marginTop: '20px' }}>
                <h3>Комментарии:</h3>
                {comments.length > 0 ? (
                  <ul>
                    {comments.map((comment) => (
                      <li key={comment.id}>{comment.text} — {new Date(comment.date).toLocaleString()}</li>
                    ))}
                  </ul>
                ) : (
                  <p>Нет комментариев</p>
                )}
              </div>
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
                position={[platform.latitude, platform.longitude]}
                eventHandlers={{
                  click: () => loadDetails(platform.id),
                }}
                icon={getIconByStatus(platform.status)}
              />
            ))}
          </MarkerClusterGroup>
        </MapContainer>
      </div>
    </div>
  );
}

export default App;