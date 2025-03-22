from http.server import HTTPServer, SimpleHTTPRequestHandler
import folium
import json
from folium.plugins import MarkerCluster

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        return super().end_headers()

def load_coordinates():
    with open("containers_coordinates.json", "r", encoding="utf-8") as file:
        return json.load(file)["containers"]

def load_container_details(container_id):
    with open("containers_details.json", "r", encoding="utf-8") as file:
        details = json.load(file)["containers"]
        return details.get(container_id, {})

def create_map():
    coords_ChelGU = [55.143029, 61.386887]
    
    m = folium.Map(location=coords_ChelGU, zoom_start=12)
    containers = load_coordinates()

    marker_cluster = MarkerCluster().add_to(m)

    for container in containers:
        container_id = container["id"]
        latitude = container["latitude"]
        longitude = container["longitude"]

        marker = folium.Marker(
            location=[latitude, longitude],
            tooltip=f"ID: {container_id}",
            icon=folium.Icon(color="red", icon="trash", prefix="fa"),
            popup=f"<button onclick='loadDetails({container_id})'>Показать детали</button>"
        )
        marker.add_to(marker_cluster)

    m.get_root().header.add_child(folium.Element("""
    <script>
    function loadDetails(containerId) {
        fetch(`http://python-app:8000/containers_details.json`)  // Обращаемся к python-app внутри Docker
            .then(response => response.json())
            .then(data => {
                const details = data.containers[containerId];
                if (details) {
                    alert(`Название: ${details.name}\\nОписание: ${details.description}\\nЗаполненность: ${details.fill_level}\\nОценка: ${details.rating}`);
                } else {
                    alert("Детали не найдены");
                }
            })
            .catch(error => alert("Ошибка при загрузке деталей"));
    }
    </script>
    """))
    m.save("frontend/public/map.html")

if __name__ == "__main__":
    create_map()

    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CORSRequestHandler)  
    print("Запуск сервера для статических файлов на порту 8000...")
    httpd.serve_forever()