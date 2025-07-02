# Pill Inspector
Uses computer vision to analyse images of pills

![Demo](https://github.com/ulhaqjackyhaw/Pill-InsectorAI/blob/main/demo/test.png?raw=true)

This Python script uses YOLOv8 and OpenCV to detect and count objects in images. 

Mainly used by nurses and pharmacists to automatically count how many count pills with their camera on their smartphone

https://github.com/user-attachments/assets/b7bb9bf3-155a-4227-90d1-eec455649747

## Training the model (optional)

https://github.com/user-attachments/assets/c22e8bd9-7867-4157-8bfb-420e0bc4b2e6

Place training images in data/images/train/

Place training labels (text files) in data/labels/train/

Place testing images in data/images/val/

Place testing labels (text files) in data/labels/val/

Ideally have a 4:1 ratio (4 times more images in training than validation)

I used Label Studio running on Docker to perform image tagging

### Create a data.yaml file (optional)

```
path: path/to/pill-inspector/data  # replace with absolute path
train: images/train
val: images/val
nc: 1  # number of classes
names: ['pill']  # class names
```
### Create a train.py file and then run it:
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
### Run the model
python3 train.py
This will create a model that we can use
model = YOLO('runs/detect/pill_inspector/weights/best.pt')

Place this into models folder

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone or download this repository to your local machine.

2. Install the required Python packages:
```bash
pip install ultralytics opencv-python numpy
```

## Usage
Run kivy script (Windows/Linux/macOS):

Run the flask script:
```bash
python3 kivy_app.py
```


Run the flask script:
```bash
python3 app.py
```
Navigate to http://127.0.0.1:5003/ if running on local machine

## Building the docker file
```bash
git clone https://github.com/ulhaqjackyhaw/Pill-InsectorAI.git
```

This will create a pill-inspector folder with this git repository contents

Change diretory into this folder and run in docker (needs sudo privileges):

```bash
sudo docker build -t pill-inspector:latest . 
```

This will create an image that we can then use.

We can then use docker-compose to run a container based on the image or we can

incorporate it with NGINX to have it running over HTTPS (needed for camera access)

To run it with NGINX, add the following to your nginx docker-compose script:

Add to nginx yaml:
```
    networks:
      - app_network
```

Add to the end of the nginx yaml:
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

Redeploy your nginx instance and it will use the pill-inspector image we created earlier and rebuild it to work with nginx

You will also need to edit your nginx configuration to have:

```
server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name pill-inspector.yourdomain.com;

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

We need SSL to work with our flask app to have camera access

Also add port 5003 to your port forwarding / ingress network rules 

Otherwise the flask app will only work locally 

## Important Notes

- The script uses YOLOv8n (nano) model which will be downloaded automatically on first run
- Default confidence threshold is set to 0.5
- Most actual pills will have a CI of 0.75 or greater

## Troubleshooting

1. If you get module import errors:
   - Make sure you've installed all required packages using pip

## Earlier Builds

https://github.com/user-attachments/assets/9cc0e65b-e74e-48a7-a3c6-ee7aed79064a
