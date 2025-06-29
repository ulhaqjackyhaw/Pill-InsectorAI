from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from ultralytics import YOLO
import cv2
import os
from datetime import datetime, timedelta
import threading
from tkinter import filedialog
import tkinter as tk
import numpy as np

class ObjectDetectionApp(App):
    def build(self):
        return ObjectDetectionLayout()

class ObjectDetectionLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Configure folders
        self.models_folder = 'models'
        self.results_folder = 'results'
        os.makedirs(self.models_folder, exist_ok=True)
        os.makedirs(self.results_folder, exist_ok=True)
        
        # Initialize model cache and webcam variables
        self.loaded_models = {}
        self.capture = None
        self.webcam_active = False
        self.showing_detection = False
        self.webcam_update_event = None
        
        # Create UI elements
        self.setup_ui()
        
        # Create hidden tkinter root for file dialog
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()
        
    def setup_ui(self):
        # Model selection spinner
        self.model_spinner = Spinner(
            text='General identification',
            values=self.get_model_names(),
            size_hint=(1, 0.1)
        )
        self.add_widget(self.model_spinner)
        
        # Image display
        self.image_display = Image(size_hint=(1, 0.6))
        self.add_widget(self.image_display)
        
        # Results label
        self.result_label = Label(
            text='No detections yet',
            size_hint=(1, 0.1)
        )
        self.add_widget(self.result_label)
        
        # Button layout
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.2),
            spacing=10
        )
        
        # Choose image button
        self.choose_button = Button(
            text='Choose Image',
            on_press=self.choose_image
        )
        button_layout.add_widget(self.choose_button)
        
        # Webcam button
        self.webcam_button = Button(
            text='Start Webcam',
            on_press=self.toggle_webcam
        )
        button_layout.add_widget(self.webcam_button)
        
        # Capture button (initially disabled)
        self.capture_button = Button(
            text='Capture Frame',
            on_press=self.capture_frame,
            disabled=True
        )
        button_layout.add_widget(self.capture_button)
        
        self.add_widget(button_layout)
    
    def get_model_names(self):
        """Get list of available models"""
        models = []
        for filename in os.listdir(self.models_folder):
            if filename.endswith('.pt'):
                base_name = os.path.splitext(filename)[0]
                if base_name == 'yolov8n':
                    display_name = 'General identification'
                else:
                    display_name = base_name.replace('_', ' ').title()
                models.append(display_name)
        return models or ['General identification']
    
    def get_model(self, display_name):
        """Load and cache the selected model"""
        if display_name == 'General identification':
            filename = 'yolov8n.pt'
        else:
            filename = display_name.lower().replace(' ', '_') + '.pt'
        
        if filename not in self.loaded_models:
            model_path = os.path.join(self.models_folder, filename)
            if not os.path.exists(model_path):
                raise ValueError(f"Model file {filename} not found")
            self.loaded_models[filename] = YOLO(model_path)
        return self.loaded_models[filename]
    
    def toggle_webcam(self, instance):
        """Toggle webcam on/off"""
        if not self.webcam_active:
            # Start webcam
            self.capture = cv2.VideoCapture(0)
            if self.capture.isOpened():
                self.webcam_active = True
                self.webcam_button.text = 'Stop Webcam'
                self.capture_button.disabled = False
                self.start_webcam_updates()
                self.result_label.text = 'Webcam active'
            else:
                self.result_label.text = 'Error: Could not open webcam'
        else:
            # Stop webcam
            self.stop_webcam()

    def start_webcam_updates(self):
        """Start webcam update schedule"""
        if self.webcam_update_event is None:
            self.webcam_update_event = Clock.schedule_interval(self.update_webcam, 1.0 / 30.0)  # 30 FPS
    
    def stop_webcam_updates(self):
        """Stop webcam update schedule"""
        if self.webcam_update_event is not None:
            self.webcam_update_event.cancel()
            self.webcam_update_event = None
    
    def stop_webcam(self):
        """Stop the webcam and clean up"""
        self.stop_webcam_updates()
        if self.capture:
            self.capture.release()
        self.webcam_active = False
        self.webcam_button.text = 'Start Webcam'
        self.capture_button.disabled = True
        self.image_display.texture = None
        self.result_label.text = 'Webcam stopped'
    
    def update_webcam(self, dt):
        """Update webcam feed"""
        if self.capture and self.webcam_active and not self.showing_detection:
            ret, frame = self.capture.read()
            if ret:
                # Flip the frame horizontally for a mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to texture
                buf = cv2.flip(frame_rgb, 0).tobytes()
                texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]), colorfmt='rgb'
                )
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                
                # Display image
                self.image_display.texture = texture
    
    def capture_frame(self, instance):
        """Capture and process current webcam frame"""
        if self.capture and self.webcam_active:
            ret, frame = self.capture.read()
            if ret:
                # Save frame temporarily
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_path = os.path.join(self.results_folder, f'capture_{timestamp}.jpg')
                cv2.imwrite(temp_path, frame)
                
                # Process the captured frame
                self.process_image(temp_path, from_webcam=True)

    def show_detection_temporarily(self, image_path):
        """Show detection result temporarily before returning to webcam feed"""
        self.showing_detection = True
        self.image_display.source = image_path
        self.image_display.reload()
        
        # Schedule return to webcam feed after 3 seconds
        Clock.schedule_once(self.return_to_webcam, 3)
    
    def return_to_webcam(self, dt):
        """Return to webcam feed after showing detection"""
        self.showing_detection = False
        self.image_display.texture = None  # Clear the current image
    
    def choose_image(self, instance):
        """Open file dialog to choose an image"""
        filepath = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            self.process_image(filepath, from_webcam=False)
    
    def process_image(self, image_path, from_webcam=False):
        """Process image with selected model"""
        try:
            # Update label to show processing
            self.result_label.text = 'Processing image...'
            
            # Get selected model
            model = self.get_model(self.model_spinner.text)
            
            # Run detection in a separate thread
            threading.Thread(target=self._run_detection, args=(model, image_path, from_webcam)).start()
            
        except Exception as e:
            self.result_label.text = f'Error: {str(e)}'
    
    def _run_detection(self, model, image_path, from_webcam):
        """Run detection in background thread"""
        try:
            # Run detection
            results = model(image_path)[0]
            
            # Count detections
            detections = len(results.boxes.data)
            
            # Save annotated image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.results_folder, f'detected_{timestamp}.jpg')
            cv2.imwrite(output_path, results.plot())
            
            # Update UI in main thread
            if from_webcam:
                Clock.schedule_once(lambda dt: self.update_results_webcam(output_path, detections))
            else:
                Clock.schedule_once(lambda dt: self.update_results(output_path, detections))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', f'Error: {str(e)}'))
    
    def update_results_webcam(self, image_path, detection_count):
        """Update results for webcam capture"""
        # Update detection count
        self.result_label.text = f'Found {detection_count} objects'
        
        # Show detection temporarily
        self.show_detection_temporarily(image_path)
    
    def update_results(self, image_path, detection_count):
        """Update results for regular image processing"""
        # Update image display
        self.image_display.source = image_path
        self.image_display.reload()
        
        # Update detection count
        self.result_label.text = f'Found {detection_count} objects'
    
    def on_stop(self):
        """Clean up resources when app is closed"""
        self.stop_webcam()

if __name__ == '__main__':
    ObjectDetectionApp().run()