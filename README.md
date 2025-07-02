
# Pill Inspector
Pill Inspector adalah aplikasi berbasis web yang dirancang untuk secara otomatis mendeteksi dan menghitung jumlah pil pada sebuah gambar. Dengan memanfaatkan teknologi AI terkini, aplikasi ini bertujuan untuk mempermudah proses inspeksi dan penghitungan pil yang seringkali memakan waktu dan rentan kesalahan jika dilakukan secara manual.

Selain kemampuan deteksi dan penghitungan pil, Pill Inspector juga dilengkapi dengan fitur deteksi gambar secara umum (general image detection). Fitur ini memungkinkan pengguna untuk mengunggah gambar apa pun dan memperoleh identifikasi objek-objek yang terdeteksi di dalamnya, seperti manusia, meja, laptop, dan lainnya. Dengan demikian, aplikasi ini tidak hanya terbatas pada inspeksi farmasi, tetapi juga dapat digunakan untuk berbagai kebutuhan pengenalan objek berbasis gambar secara luas

![Demo](https://github.com/ulhaqjackyhaw/Pill-InsectorAI/blob/main/demo/test.png?raw=true)

Script Python ini menggunakan YOLOv8 dan OpenCV untuk mendeteksi dan menghitung objek pada gambar.

Utamanya digunakan oleh perawat dan apoteker untuk menghitung jumlah pil secara otomatis menggunakan kamera.

## FITUR 1
Deteksi & Hitung Pil Otomatis, klik gambar untuk lihat demo

[![Demo Video](https://img.youtube.com/vi/UUzrEuUZKno/0.jpg)](https://www.youtube.com/watch?v=UUzrEuUZKno)


## FITUR 2
Deteksi Objek Secara Umum, klik gambar untuk lihat demo

[![Demo Video](https://img.youtube.com/vi/Vpcpp57HaKo/0.jpg)](https://www.youtube.com/watch?v=Vpcpp57HaKo)


## Melatih Model (Opsional)

https://github.com/user-attachments/assets/c22e8bd9-7867-4157-8bfb-420e0bc4b2e6

Letakkan gambar pelatihan di `data/images/train/`

Letakkan label pelatihan (file .txt) di `data/labels/train/`

Letakkan gambar validasi di `data/images/val/`

Letakkan label validasi di `data/labels/val/`

Idealnya rasio data train:val = 4:1 (4x lebih banyak gambar pelatihan)

Saya menggunakan Label Studio (Docker) untuk melakukan penandaan gambar

### Contoh data.yaml (Opsional)

```
path: path/to/pill-inspector/data  # ganti dengan path absolut
train: images/train
val: images/val
nc: 1  # jumlah kelas
names: ['pill']  # nama kelas
```
### Contoh train.py lalu jalankan:
```
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model.train(
    data='data.yaml',
    epochs=100,
    imgsz=640,
    batch=8,
    name='pill_inspector'
)
```
### Menjalankan model
python3 train.py
Ini akan menghasilkan model yang bisa digunakan
model = YOLO('runs/detect/pill_inspector/weights/best.pt')

Tempatkan file model ke folder `models`

## Prasyarat

- Python 3.8 atau lebih baru
- pip (Python package installer)

## Instalasi

1. Clone atau unduh repository ini ke komputer Anda.

2. Install package Python yang dibutuhkan:
```bash
pip install ultralytics opencv-python numpy
```

## Penggunaan
Jalankan script Kivy (Windows/Linux/macOS):

Jalankan script Flask:
```bash
python3 kivy_app.py
```

Atau jalankan script Flask:
```bash
python3 app.py
```
Lalu buka http://127.0.0.1:5003/ jika dijalankan secara lokal

## Build Docker
```bash
git clone https://github.com/ulhaqjackyhaw/Pill-InsectorAI.git
```

Ini akan membuat folder pill-inspector berisi isi repository ini

Masuk ke folder tersebut dan build docker (butuh sudo):

```bash
sudo docker build -t pill-inspector:latest . 
```

Ini akan membuat image yang bisa digunakan.

Bisa dijalankan dengan docker-compose atau digabung dengan NGINX agar bisa HTTPS (perlu untuk akses kamera)

Untuk menjalankan dengan NGINX, tambahkan ke docker-compose nginx:

Tambahkan ke yaml nginx:
```
    networks:
      - app_network
```

Tambahkan di akhir yaml nginx:
```
  flask_app:
    image: pill-inspector:latest
    container_name: flask-app
    environment:
      - FLASK_ENV=production
    ports:
      - "5003:5003"
    networks:
      - app_network
    depends_on:
      - swag
    restart: unless-stopped

networks:
  app_network:
    driver: bridge
```

Redeploy nginx Anda agar menggunakan image pill-inspector yang sudah dibuat

Edit juga konfigurasi nginx Anda:

```
server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name pill-inspector.domainanda.com;

    include /config/nginx/ssl.conf;

    client_max_body_size 0;

    location / {
        include /config/nginx/proxy.conf;
        set $upstream_app flask-app;
        set $upstream_port 5003;
        set $upstream_proto http;
        proxy_pass $upstream_proto://$upstream_app:$upstream_port;
    }
}
```

SSL diperlukan agar flask app bisa akses kamera

Jangan lupa buka port 5003 di firewall/port forwarding

Jika tidak, flask app hanya bisa diakses lokal

## Catatan Penting

- Script menggunakan model YOLOv8n (nano) yang akan otomatis diunduh saat pertama kali dijalankan
- Confidence threshold default 0.5
- Kebanyakan pil asli akan punya CI >= 0.75

## Troubleshooting

1. Jika ada error import modul:
   - Pastikan semua package sudah diinstall dengan pip



