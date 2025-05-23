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

const greyIcon = new L.Icon({
  iconUrl: '/images/grey_marker.png',
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
  const [filterStatus, setFilterStatus] = useState(null); // null — показать все
  const [stats, setStats] = useState({ green: 0, yellow: 0, red: 0 });
  const [file, setFile] = useState(null);

  const backendUrl = 'https://primary-happily-worm.ngrok-free.app';
  const renameFile = (file, platformId) => {
    const extension = file.name.split('.').pop(); // Получаем расширение файла (например, 'jpg')
    const newFileName = `${platformId}.${extension}`; // Создаем новое имя файла с ID платформы
    return new File([file], newFileName, { type: file.type });
  };

  useEffect(() => {
    const fetchPlatforms = async () => {
      try {
        let url = `${backendUrl}/platforms`;
        if (filterStatus) {
          url = `${backendUrl}/platforms/filter/?status=${filterStatus}`;
        }
  
        const response = await axios.get(url, {
          headers: {    'ngrok-skip-browser-warning': '69420'
          }});
        const platformsData = response.data.platforms.map((platform) => ({
          ...platform,
          image: `${backendUrl}/platform_photo/${platform.id}`,
        }));
        setPlatforms(platformsData);
      } catch (error) {
        console.error("Ошибка при загрузке данных:", error);
      }
    };
      
    const fetchStats = async () => {
      try {
        const statsResponse = await axios.get(`${backendUrl}/platforms/stats`, {headers: {'ngrok-skip-browser-warning': '69420'}});
        setStats(statsResponse.data);
      } catch (error) {
        console.error("Ошибка при загрузке статистики:", error);
      }
    };
  
    fetchPlatforms();
    fetchStats();
  }, [filterStatus]);

  const loadDetails = async (id) => {
    try {
      //const formattedId = formatId(id); // форматируем ID
      const formattedId = id; // форматируем ID
  
      // Загружаем основную информацию о платформе
      const response = await axios.get(`${backendUrl}/platform_info/${formattedId}`, {
        params: { item_id: formattedId }, headers: {'ngrok-skip-browser-warning': '69420'}
      });
  
      const platform = response.data;
  
      if (platform) {
        let imageUrl = null;
  
        // Пытаемся загрузить фото, но не падаем, если его нет
        try {
          const imageResponse = await axios.get(`${backendUrl}/platform_photo/${formattedId}`, {
            responseType: 'blob',
            headers: {'ngrok-skip-browser-warning': '69420'}
          });
          
          imageUrl = URL.createObjectURL(imageResponse.data);
        } catch (imageError) {
          console.warn("Фото не найдено:", imageError);
          // Если фото не найдено — просто продолжаем без него
        }
  
        // Получаем комментарии
        const commentsResponse = await axios.get(`${backendUrl}/comments/${formattedId}`, {headers: {'ngrok-skip-browser-warning': '69420'}});
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
        `${backendUrl}/comments/${selectedPlatform.id}`, {headers: {'ngrok-skip-browser-warning': '69420'}}, // Используем правильный эндпоинт
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

  const handleSubmitPhoto = async (event) => {
    event.preventDefault();
    if (!selectedPlatform || !file) {
      alert('Выберите платформу и файл для загрузки');
      return;
    }

    try {
      const renamedFile = renameFile(file, selectedPlatform.id); // Получаем переименованный файл

      const formData = new FormData();
      formData.append('file', renamedFile); // Используем переименованный файл

      const response = await axios.post(
        `${backendUrl}/platform_photo/${selectedPlatform.id}`, 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data', 
            'ngrok-skip-browser-warning': '69420'
          }
        }
      );

      // После успешной загрузки, обновляем URL фото
      setSelectedPlatform((prev) => ({
        ...prev,
        image: `${backendUrl}/platform_photo/${selectedPlatform.id}`
      }));

      alert('Фото успешно загружено!');
    } catch (error) {
      console.error("Ошибка при загрузке фото:", error);
      alert('Не удалось загрузить фото');
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
        return greyIcon; // Серый цвет по умолчанию
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
              {/* Отображение даты изменения */}
              {selectedPlatform.change !== "-" && (
                <p style={{ marginTop: '8px', fontStyle: 'italic', color: '#666' }}>
                  Последнее изменение: {selectedPlatform.change}
                </p>
              )}
              {/* Форма для отправки комментария */}
              <div style={{ marginTop: '20px' }}>
                <h3>Добавить комментарий</h3>
                <form onSubmit={handleSubmitComment} style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px'
                }}>
                  <input
                    type="text"
                    placeholder="Введите ваш комментарий..."
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    required
                    style={{
                      padding: '10px',
                      borderRadius: '6px',
                      border: '1px solid #ccc',
                      fontSize: '14px',
                      width: '100%',
                      boxSizing: 'border-box',
                      outline: 'none',
                      transition: 'border-color 0.3s ease',
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#007bff'}
                    onBlur={(e) => e.target.style.borderColor = '#ccc'}
                  />
                  <button
                    type="submit"
                    style={{
                      padding: '10px 15px',
                      background: 'linear-gradient(to right, #007bff, #0056b3)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                      transition: 'background 0.3s ease',
                    }}
                    onMouseOver={(e) => {
                      e.target.style.background = 'linear-gradient(to right, #0056b3, #004085)';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = 'linear-gradient(to right, #007bff, #0056b3)';
                    }}
                  >
                    Отправить
                  </button>
                </form>
              </div>
              {/* Отображение существующих комментариев */}
              <div style={{ marginTop: '20px' }}>
                <h3>Комментарии</h3>
                {comments.length > 0 ? (
                  <ul style={{
                    listStyle: 'none',
                    paddingLeft: 0,
                    maxHeight: '200px',
                    overflowY: 'auto',
                    border: '1px solid #eee',
                    borderRadius: '6px',
                    padding: '10px',
                    backgroundColor: '#f9f9f9',
                  }}>
                    {comments.map((comment) => (
                      <li key={comment.id} style={{
                        backgroundColor: '#fff',
                        padding: '10px',
                        marginBottom: '10px',
                        borderRadius: '6px',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        position: 'relative',
                      }}>
                        <p style={{ margin: '0 0 5px', fontSize: '14px' }}><strong>{comment.text}</strong></p>
                        <small style={{ color: '#888', fontSize: '12px' }}>
                          {new Date(comment.date).toLocaleString()}
                        </small>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontStyle: 'italic', color: '#999' }}>Нет комментариев</p>
                )}
              </div>
              <div style={{ marginTop: '20px' }}>
                <h3>Загрузить фото мусорки</h3>
                <form onSubmit={handleSubmitPhoto}>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFile(e.target.files[0])}
                    required
                  />
                  <button type="submit" disabled={!file}>
                    Загрузить
                  </button>
                </form>
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
          {/* Панель фильтрации и статистики */}
          <div style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            zIndex: 1000,
            backgroundColor: 'white',
            padding: '10px',
            borderRadius: '8px',
            boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
          }}>
            <h4 style={{ margin: '0 0 10px', textAlign: 'center' }}>Фильтр</h4>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <button
                onClick={() => setFilterStatus(null)}
                style={{ background: filterStatus === null ? '#007bff' : '#ddd', color: filterStatus === null ? 'white' : 'black', border: 'none', padding: '5px 10px', cursor: 'pointer' }}
              >
                Все
              </button>
              <button
                onClick={() => setFilterStatus('green')}
                style={{ background: filterStatus === 'green' ? 'green' : '#ddd', color: filterStatus === 'green' ? 'white' : 'black', border: 'none', padding: '5px 10px', cursor: 'pointer' }}
              >
                Зелёные ({stats.green})
              </button>
              <button
                onClick={() => setFilterStatus('yellow')}
                style={{ background: filterStatus === 'yellow' ? 'orange' : '#ddd', color: filterStatus === 'yellow' ? 'white' : 'black', border: 'none', padding: '5px 10px', cursor: 'pointer' }}
              >
                Жёлтые ({stats.yellow})
              </button>
              <button
                onClick={() => setFilterStatus('red')}
                style={{ background: filterStatus === 'red' ? 'red' : '#ddd', color: filterStatus === 'red' ? 'white' : 'black', border: 'none', padding: '5px 10px', cursor: 'pointer' }}
              >
                Красные ({stats.red})
              </button>
            </div>
          </div>

          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
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