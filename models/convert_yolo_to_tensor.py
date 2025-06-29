# Doesn't work really well, I recommend running node.js (Version 18 ideally but <=22)
# And training a model with tensorflow.js

from ultralytics import YOLO

# Load your existing YOLO model
model = YOLO('pill_inspection_new_version.pt')

# Export to TensorFlow.js format
model.export(format='tfjs')