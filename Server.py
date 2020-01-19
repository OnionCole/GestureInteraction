"""
CODE WRITTEN BY:
Cole Mameesh Anderson



"""

# IMPORTS
from flask import Flask
from flask import request
from jinja2 import Template
import threading
import cv2
import time
import os
import ast
import traceback

# from Gesture_Detection import gesture_detection
gesture_detection = lambda x: 0  # TODO: use the above imported method

# HARDCODED VARIABLES
# TODO: think about using a config
HOST = "127.0.0.1"
PORT = "4001"

AUTO_REFRESH_SECONDS = 1
auto_refresh_milliseconds = AUTO_REFRESH_SECONDS * 1000
MENU = ["Cheese", "Tomato", "Onions", "Pickles", "Ketchup"]
menu_len = len(MENU)


# FUNCTIONS
def get_user_input():
    remote_address = request.remote_addr  # request.headers['X-Real-IP']

    # determine the path to save the file to
    img_path = str(time.time()) + " " + str(remote_address) + '.png'  # generate a path using both the current timestamp and the ip of the sender
    # TODO: could make while loop to be completely sure the path is unique

    # get the webcam picture
    camera = cv2.VideoCapture(0)
    return_value, image = camera.read()
    cv2.imwrite(img_path, image)

    # get the gesture output
    gesture_output = gesture_detection(img_path)

    # delete the image file
    os.remove(img_path)

    return gesture_output


def number_list_to_string(l) -> str:
    return str(l)[1:-1].replace(' ', '').replace(',', 'q')


def string_to_number_list(s) -> list:
    return ast.literal_eval("[" + s.replace('q', ',') + "]")


# ROUTE SETUP
app = Flask(__name__)


@app.route('/', methods=['GET'], endpoint='main_page')
def main_page():
    # get args
    first = not request.args.get("f", '')  # is this the first ping
    total_input = request.args.get("ti", '')  # total input so far
    try:
        total_input = string_to_number_list(total_input)
    except:  # TODO: add exceptions to be clean
        print(traceback.format_exc())
        total_input = []
    total_input_len = len(total_input)

    if total_input_len >= menu_len:  # if we have received all the input we want

        # template
        page_to_serve = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GestureInteraction</title>
</head>
<body>
    Your Input Was:
    {{total_input}}
</body>
</html>
        """)

        return page_to_serve.render(total_input=str(total_input))
    else:  # we need more input

        # determine display for next item
        next_item = None if total_input_len + 1 >= menu_len else MENU[total_input_len + (0 if first else 1)]

        # get user input
        if not first:
            total_input.append(get_user_input())  # if the index is 0, we need to show the user what we are asking before we take an image

        # template
        page_to_serve = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GestureInteraction</title>
</head>
<body>

    next_item:
    {{next_item}}
    
    <form id="var_form" method="GET">
        <input type="hidden" name="f" value="F">
        <input type="hidden" name="ti" value={{total_input}}>
    </form>
    
    <script>
        var load = setTimeout( function() {
            document.getElementById("var_form").submit();
        }, {{auto_refresh_milliseconds}});
    </script>

</body>
</html>
        """)
        return page_to_serve.render(auto_refresh_milliseconds=auto_refresh_milliseconds, total_input=number_list_to_string(total_input), next_item=next_item)


@app.route('/simple', methods=['GET'], endpoint='simple')
def simple():
    # get user input
    gesture_output = get_user_input()

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

    return page_to_serve.render(auto_refresh_seconds=AUTO_REFRESH_SECONDS, gesture_output=gesture_output)


# MAIN
flask_server = threading.Thread(target=lambda: app.run(host=HOST, port=PORT, debug=False))
flask_server.start()

# TODO: add background color
# TODO: consider adding READY_TO_SERVE mechanism for trying to access the page before it has loaded
# TODO: clean up imports
# TODO: do method comments

# TODO: consider noting all dependencies (opencv-python)
