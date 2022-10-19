import numpy as np
import cv2
import time
from datetime import datetime
import csv
from time import sleep

#_____________
def gstreamer_pipeline(
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

#________
try:
    from gps import GPS
except:
    class GPS():
        lat = 0.0
        lon = 0.0


# start the gps and create the coordinates file
gps = GPS()
filename = datetime.now().strftime("/media/pendrive/gps/%Y-%m-%d_%H:%M:%S.csv")
fieldnames = ['timestamp', 'latitude', 'longitude']
csvfile = open(filename, 'w')
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()
csvfile.close()
coordinates = []
last_gps_query = time.time()

# start the video
cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture(0)
fps = 5.6
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)
video_codec = cv2.VideoWriter_fourcc(*'mp4v')
# The duration in seconds of the video captured
capture_duration = 180  #(for capture_duration = 500 I had a video of 10.24 minute and for capture_duration = 600 I had a video of 12.29 minute)
start = time.time()
video_file_count = 1
name = datetime.now().strftime("/media/pendrive/data/%Y-%m-%d_%H-%M-%S.mp4")
# Create a video write before entering the loop
video_writer = cv2.VideoWriter(
    name, video_codec, fps, size)

while cap.isOpened():
    ret, frame = cap.read()
    if ret == True:
        now = time.time()
        if now - last_gps_query >= 5: # get gps coordinates every 5s
            dict = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'latitude': gps.lat,
                'longitude': gps.lon,
            }
            coordinates.append(dict)
            last_gps_query = now

        if now - start >= capture_duration :
            start = now
            video_file_count += 1
            name = datetime.now().strftime("/media/pendrive/data/%Y-%m-%d_%H-%M-%S.mp4")
            video_writer = cv2.VideoWriter(name, video_codec, fps, size)
            # write the coordinates to the file
            csvfile = open(csvfile.name, 'a')
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for coordinate in coordinates:
                writer.writerow(coordinate)
            csvfile.close()

        # Write the frame to the current video writer
        video_writer.write(frame)
    else:
        break
cap.release()
cv2.destroyAllWindows()


