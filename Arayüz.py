import tkinter as tk
from tkinter import ttk
from tkinter import Label, PhotoImage
from PIL import Image, ImageTk
import sqlite3
import io
import webbrowser

# Connect to SQLite database
conn = sqlite3.connect('pothole_detection.db')
cursor = conn.cursor()

# Fetch data from the database
cursor.execute('SELECT image, timestamp, latitude, longitude, map_link FROM detections')
data = cursor.fetchall()

# Function to open the map link in a web browser
def open_map_link(url):
    webbrowser.open(url, new=2)

# Create the main window
root = tk.Tk()
root.title("Pothole Detection Viewer")
root.geometry("800x600")

# Create a treeview to list detections
tree = ttk.Treeview(root, columns=("Timestamp", "Latitude", "Longitude", "Map Link"), show='headings')
tree.heading("Timestamp", text="Timestamp")
tree.heading("Latitude", text="Latitude")
tree.heading("Longitude", text="Longitude")
tree.heading("Map Link", text="Map Link")

# Insert data into the treeview
for i, (image, timestamp, latitude, longitude, map_link) in enumerate(data):
    tree.insert('', 'end', values=(timestamp, latitude, longitude, map_link))

tree.pack(expand=True, fill='both')

# Create a label to show the image
image_label = Label(root)
image_label.pack()

# Function to show the selected detection
def show_detection(event):
    selected_item = tree.selection()[0]
    selected_data = tree.item(selected_item, 'values')
    timestamp, latitude, longitude, map_link = selected_data

    # Fetch the corresponding image from the database
    cursor.execute('SELECT image FROM detections WHERE timestamp=? AND latitude=? AND longitude=? AND map_link=?',
                   (timestamp, latitude, longitude, map_link))
    image_data = cursor.fetchone()[0]
    image = Image.open(io.BytesIO(image_data))
    image = ImageTk.PhotoImage(image)

    # Update the image label
    image_label.config(image=image)
    image_label.image = image

    # Update the map link button
    map_link_button.config(command=lambda: open_map_link(map_link))

# Bind the treeview selection event to the show_detection function
tree.bind('<<TreeviewSelect>>', show_detection)

# Create a button to open the map link
map_link_button = tk.Button(root, text="Open Map Link")
map_link_button.pack()

# Start the main event loop
root.mainloop()

# Close the database connection
conn.close()

