from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# Configure upload folder and models folder
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODELS_FOLDER'] = 'models'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['MAX_FILE_AGE'] = timedelta(hours=24)  # Maximum age for uploaded files

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODELS_FOLDER'], exist_ok=True)

# Dictionary to store loaded models
loaded_models = {}

def cleanup_old_files():
    """Remove files older than MAX_FILE_AGE from the upload folder"""
    current_time = datetime.now()
    cleanup_count = 0
    
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            # Get file modification time
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            # Remove if file is older than MAX_FILE_AGE
            if current_time - file_time > app.config['MAX_FILE_AGE']:
                os.remove(filepath)
                cleanup_count += 1
                
        except (OSError, ValueError) as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    if cleanup_count > 0:
        print(f"Cleaned up {cleanup_count} old files")

def get_available_models():
    """Scan the models folder for .pt files and format their display names"""
    models = []
    for filename in os.listdir(app.config['MODELS_FOLDER']):
        if filename.endswith('.pt'):
            base_name = os.path.splitext(filename)[0]
            if base_name == 'yolov8n':
                display_name = 'General identification'
            else:
                # Capitalize first letter and replace underscores with spaces
                display_name = base_name.replace('_', ' ').title()
            models.append({
                'filename': filename,
                'display_name': display_name
            })
    return models

def get_model(model_filename):
    """Get or load the requested model"""
    
    if model_filename not in loaded_models:
        model_path = os.path.join(app.config['MODELS_FOLDER'], model_filename)
        if not os.path.exists(model_path):
            raise ValueError(f"Model file {model_filename} not found")
        loaded_models[model_filename] = YOLO(model_path)
    return loaded_models[model_filename]

@app.route('/')
def home():
    models = get_available_models()
    return render_template('index.html', models=models)

@app.route('/detect', methods=['POST'])
def detect():
    # Clean up old files before processing new upload
    cleanup_old_files()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get selected model and confidence level from form data
    model_filename = request.form.get('model', 'yolov8n.pt')
    confidence_level = float(request.form.get('confidence', 0.7))  # Default to 0.7 if not specified
    
    try:
        # Load the appropriate model
        model = get_model(model_filename)
        
        # Save the uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'capture_{timestamp}.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run detection
        results = model(filepath, conf=confidence_level)[0]  # Use the specified confidence level
        
        # Count detections
        detections = len(results.boxes.data)
        
        # Save annotated image
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'detected_' + filename)
        cv2.imwrite(output_path, results.plot())
        
        return jsonify({
            'count': detections,
            'image': 'detected_' + filename
        })
        
    except Exception as e:
        return jsonify({'error': "Uh oh..." + str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Optional: Add a manual cleanup endpoint for testing
@app.route('/cleanup', methods=['POST'])
def manual_cleanup():
    cleanup_old_files()
    return jsonify({'message': 'Cleanup completed'})

if __name__ == "__main__":
    cleanup_old_files()
    app.run(host='0.0.0.0', port=5003, debug=False) 