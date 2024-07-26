import sqlite3
import cv2
import numpy as np

# Connect to SQLite database
conn = sqlite3.connect('pothole_detection.db')
cursor = conn.cursor()

# Query to fetch all records from the detections table
query = 'SELECT id, image, timestamp FROM detections'

# Execute the query
cursor.execute(query)

# Fetch all results
rows = cursor.fetchall()

for row in rows:
    id, image_blob, timestamp = row
    # Convert binary data back to an image
    nparr = np.frombuffer(image_blob, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Display the image
    cv2.imshow(f'Image ID: {id}', image)
    print(f'ID: {id}, Timestamp: {timestamp}')

    # Wait for a key press and then close the image window
    cv2.waitKey(0)
    cv2.destroyWindow(f'Image ID: {id}')

# Close the database connection
conn.close()
