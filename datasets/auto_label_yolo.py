from ultralytics import YOLO
import os
import cv2

# Path ke model YOLO yang sudah ada (bisa ganti ke model custom jika mau)
MODEL_PATH = '../models/yolov8n.pt'  # atau ganti ke model lain
IMAGES_DIR = '../images/original_quality'  # folder gambar mentah
LABELS_DIR = '../auto_labels'  # folder output label

CONFIDENCE = 0.5  # threshold deteksi

os.makedirs(LABELS_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)

for filename in os.listdir(IMAGES_DIR):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(IMAGES_DIR, filename)
        results = model(img_path, conf=CONFIDENCE)[0]
        h, w = cv2.imread(img_path).shape[:2]
        label_lines = []
        for box in results.boxes:
            cls = 0  # Selalu class 0
            x1, y1, x2, y2 = box.xyxy[0]
            # Konversi ke format YOLO (x_center, y_center, width, height) relatif
            x_center = ((x1 + x2) / 2) / w
            y_center = ((y1 + y2) / 2) / h
            width = (x2 - x1) / w
            height = (y2 - y1) / h
            label_lines.append(f"{cls} {x_center} {y_center} {width} {height}")
        # Simpan file label
        label_path = os.path.join(LABELS_DIR, os.path.splitext(filename)[0] + '.txt')
        with open(label_path, 'w') as f:
            f.write('\n'.join(label_lines))
        print(f"Label untuk {filename} disimpan di {label_path}")

print("Selesai auto-labeling!")
