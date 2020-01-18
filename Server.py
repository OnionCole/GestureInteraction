"""
CODE WRITTEN BY:
Cole Mameesh Anderson



"""

# IMPORTS
from flask import Flask
from flask import request
import urllib.request
from jinja2 import Template
import threading
import cv2
import time
import os

from Gesture_Detection import gesture_detection


# HARDCODED VARIABLES
# TODO: think about using a config
HOST = "127.0.0.1"
PORT = "4001"

AUTO_REFRESH_SECONDS = 5


# ROUTE SETUP
app = Flask(__name__)

@app.route('/', methods=['GET'], endpoint='main_page')
def main_page():

    # determine the path to save the file to
    img_path = str(time.time()) + " " + str(request.remote_addr) + '.png'  # generate a path using both the current timestamp and the ip of the sender
    # TODO: could make while loop to be completely sure the path is unique

    # get the webcam picture
    camera = cv2.VideoCapture(0)
    return_value, image = camera.read()
    cv2.imwrite(img_path, image)

    # get the gesture output
    gesture_output = gesture_detection(img_path)

    # delete the image file
    os.remove(img_path)

    # template
    page_to_serve = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GestureInteraction</title>
    <meta http-equiv="refresh" content={{auto_refresh_seconds}}>
</head>
<body>
    {{gesture_output}}
</body>
</html>
""")

    return page_to_serve.render(auto_refresh_seconds=5, gesture_output=gesture_output)


# MAIN
flask_server = threading.Thread(target=lambda: app.run(host=HOST, port=PORT, debug=False))
flask_server.start()

# TODO: add background color
# TODO: consider adding READY_TO_SERVE mechanism for trying to access the page before it has loaded
# TODO: clean up imports

# TODO: consider noting all dependencies (opencv-python)
