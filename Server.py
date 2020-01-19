"""
CODE WRITTEN BY:
Cole Mameesh Anderson



"""

# IMPORTS
from flask import Flask
from flask import request
from jinja2 import Template
from flask import render_template
import threading
import cv2
import time
import os
import ast
import traceback

from Messenger import Messenger


from Gesture_Detection import gesture_detection
#gesture_detection = lambda x: 0  # TODO: use the above imported method

# HARDCODED VARIABLES
# TODO: think about using a config
HOST = "127.0.0.1"
PORT = "4001"
CONTACT = "msmith17@berkeley.edu"  # where the emails are being sent

AUTO_REFRESH_SECONDS = 5
auto_refresh_milliseconds = AUTO_REFRESH_SECONDS * 1000
MENU = [("Drink", ["Coke", "Water", "Milk", "Wine"]),
        ("Appetizer", ["Crab Cakes", "Spring Rolls", "Cheese", "Bread and Butter", "Brussel Sprouts"]),
        ("Main", ["Prime Rib", "Cheese Burger", "Spaghetti", "Sandwhich", "Ham"]),
        ("Dessert", ["Cheesecake", "Creme Brule", "Brownie", "Banana Split", "Ice Cream Sundae"])]
menu_len = len(MENU)
C_MENU = ("Main",
                {"Hotdog": ("Toppings",
                                    {"Ketchup": None, "Sauerkraut": None}),
                "Prime Rib": ("Sides",
                                    {"Creamed Corn": None})})


# FUNCTIONS
def get_user_input() -> int:
    """
    Takes a picture using the webcam and gets a number representing the gesture from it
    Should only be called from an @app.route method, since it references request to get the sender IP
    :return: The number which represents the gesture in the picture taken
    """
    remote_address = request.remote_addr  # request.headers['X-Real-IP']

    # determine the path to save the file to
    img_path = str(time.time()) + " " + str(remote_address) + '.png'  # generate a path using both the current timestamp and the ip of the sender
    # TODO: could make while loop to be completely sure the path is unique

    # get the webcam picture
    camera = cv2.VideoCapture(0)
    for _ in range(10):
        return_value, image = camera.read()

    # reduce image to easy parse
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (7, 7), 3)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    ret, final_image = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # write to png file
    cv2.imwrite(img_path, final_image)

    # get the gesture output
    gesture_output = gesture_detection(img_path)

    # delete the image file
    os.remove(img_path)

    return gesture_output


def number_list_to_string(l) -> str:
    """
    Convert a certain type of list to an all letters and digits string that can be parsed back into a list
    :param l: list whose only elements are of type int
    :return: str representation of l with brackets stripped and commas replaced by a letter
    """
    return str(l)[1:-1].replace(' ', '').replace(',', 'q')


def string_to_number_list(s) -> list:
    """
    Convert an output of number_list_to_string back into a list
    :param s: an output of number_list_to_string
    :return: the list represented by the string
    """
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

    # get user input
    if not first:
        total_input.append(get_user_input())  # if the index is 0, we need to show the user what we are asking before we take an image

    if len(total_input) >= menu_len:  # if we have received all the input we want

        # send an email off with the input
        #create list of order based on total_input and MENU
        options = []
        for i in range(len(MENU)):
            if total_input[i] != 0 and total_input[i] <= len(MENU[i][1]):
                options.append(MENU[i][1][total_input[i] - 1])

        message = "A client has ordered "
        first = True
        for option in options:
            if first:
                first = False
                message += option
            else:
                message += ", " + option
        message += "."
        print(message)

        Messenger(contact=CONTACT, msg=message).send()  # TODO: probably? should spin a thread for this so return can happen quickly

        return render_template('receipt.html', total_input=str(total_input), orders=options)

    # determine display for next item
    next_item_title, next_item_list = MENU[len(total_input)]

    # we need more input
    return render_template('menu.html', title=next_item_title, options=next_item_list, auto_refresh_seconds=AUTO_REFRESH_SECONDS, still_first="F",
            total_input=number_list_to_string(total_input))


@app.route('/causal', methods=['GET'], endpoint='causal_page')
def causal_page():

    # get args
    first = not request.args.get("f", '')  # is this the first ping
    keep_first = False
    total_input = request.args.get("ti", '')  # total input so far
    try:
        total_input = string_to_number_list(total_input)
    except:  # TODO: add exceptions to be clean
        print(traceback.format_exc())
        total_input = []

    # get user input
    if not first:
        total_input.append(get_user_input())  # if the index is 0, we need to show the user what we are asking before we take an image

    # determine display for next item
    # TODO: is the below proper clean?
    try:
        if len(total_input) > 0:
            assert total_input[-1] != 0
        found_tuple = C_MENU
        for input_value in total_input:
            found_tuple = found_tuple[1][list(found_tuple[1].keys())[input_value - 1]]
    except (AssertionError, KeyError, IndexError):  # we got an unacceptable input
        total_input.pop()
        found_tuple = C_MENU
        for input_value in total_input[:-1]:
            found_tuple = found_tuple[1][list(found_tuple[1].keys())[input_value - 1]]
        if first:
            keep_first = True

    if found_tuple is None:  # if we have received all the input we want

        # template
        page_to_serve = Template("""<!DOCTYPE html>
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

        # send an email off with the input
        Messenger(contact=CONTACT, msg=str(total_input)).send()  # TODO: probably? should spin a thread for this so return can happen quickly

        return page_to_serve.render(total_input=str(total_input))

    # we need more input

    next_item_title, next_item_list = found_tuple

    return render_template('menu.html', title=next_item_title, options=next_item_list, auto_refresh_seconds=AUTO_REFRESH_SECONDS, still_first="" if keep_first else "F",
            total_input=number_list_to_string(total_input))


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
