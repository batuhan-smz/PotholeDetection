import time
import serial
import cv2
from ultralytics import YOLO
from datetime import datetime
import sqlite3  # For database operations

# Load the YOLOv8 model
model = YOLO('runs/detect/train/weights/best.pt')

# Initialize serial
ser = serial.Serial("COM3", 9600)  # Doğru COM portunu kullandığınızdan emin olun

# Initialize camera
cap = cv2.VideoCapture(0)

# Create or connect to SQLite database
conn = sqlite3.connect('pothole_detection.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image BLOB,
    timestamp TEXT,
    latitude TEXT,
    longitude TEXT,
    map_link TEXT
)
''')
conn.commit()


def image_to_blob(image):
    """Convert an image to binary data."""
    success, encoded_image = cv2.imencode('.jpg', image)
    return encoded_image.tobytes() if success else None


def read_gps_data():
    """Read GPS data from the serial port."""
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        lat, lon = line.split(" Lon: ")
        latitude = lat.split("Lat: ")[1]
        longitude = lon
        return latitude, longitude
    return None, None


def generate_map_link(latitude, longitude):
    """Generate a Google Maps link for the given coordinates."""
    return f"https://www.google.com/maps?q={latitude},{longitude}"


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform detection with the model
    results = model(frame)

    # Extract results using bbox
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Extract information from the box
                x1, y1, x2, y2 = box.xyxy[0].tolist()  # Coordinates of the bounding box
                confidence = box.conf[0]  # Confidence score
                cls = box.cls[0]  # Class index

                # Get class name from class index if necessary
                label = model.names[int(cls)]

                if label == 'hole' and confidence > 0.5:  # Adjust confidence threshold as needed
                    # Draw bounding box on the frame
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                    # Add label text
                    label_text = f'{label} {confidence:.2f}'
                    cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                                2)

                    # Convert the frame to binary data
                    image_blob = image_to_blob(frame)

                    # Read GPS data
                    latitude, longitude = read_gps_data()
                    map_link = generate_map_link(latitude, longitude)

                    # Save the image, timestamp, and location in the database
                    now = datetime.now()
                    cursor.execute('''
                    INSERT INTO detections (image, timestamp, latitude, longitude, map_link)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (image_blob, now.strftime('%Y-%m-%d %H:%M:%S'), latitude, longitude, map_link))
                    conn.commit()

                    print(f'Pothole detected and data saved in the database.')

                    # Wait for a while before the next detection to avoid duplicates
                    time.sleep(5)
                    break

    # Display the frame with bounding boxes
    cv2.imshow('Frame', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
conn.close()
ser.close()
