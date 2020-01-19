# GestureInteraction

## General

System to take input from humans through hand gestures made before a webcam.

Flask serves a webpage where this input may be taken.

OpenCV is used to take a picture from a webcam.

Google Cloud automl is used to parse a hand gesture into an element of the set {0, 1, 2, 3, 4, 5}.

User can be prompted for input from a list of multiple choice questions or from a tree of multiple choice questions where
		one answer leads to a set of mutiple choice options.

Notivize is used to email list of user's input "reciept" once all input is taken.

## Setup
### Pip Package Dependencies

pip install --upgrade google-cloud-vision
pip install google-cloud-automl
pip install opencv-python

### Other Setup

For GCloud installation, follow the instructions at this URL:
https://cloud.google.com/sdk/docs/


## Credit

Thanks to jaredvasquez for his dataset and code regarding the reduction of color images to fit his dataset.
https://github.com/jaredvasquez/CNN-HowManyFingers

Note: jaredvasquez did not inspire this project, nor the use of the opencv-python module, nor any other piece of our project. 
		His work was found after our dependencies and general structure were already decided upon. The sole elements of his work 
		used by this project are his dataset and his code regarding the reduction of color images to fit his dataset.
