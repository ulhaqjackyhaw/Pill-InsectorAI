from ultralytics import YOLO

# Load a pretrained model
model = YOLO('yolov8n.pt')

# Train the model
results = model.train(
    data='data.yaml',
    epochs=100,
    imgsz=640,
    batch=8,
    name='pill_detector'
)