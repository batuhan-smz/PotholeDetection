import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('pothole_detection.db')
cursor = conn.cursor()

# Drop the existing table if it exists
cursor.execute("DROP TABLE IF EXISTS detections")

# Create the table with the correct schema
cursor.execute('''
CREATE TABLE detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image BLOB,
    timestamp TEXT
    latitude TEXT
    longtitude TEXT
    map_link TEXT
)
''')

conn.commit()
conn.close()
