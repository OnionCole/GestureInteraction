from google.cloud import automl

def gesture_detection(file_path):
    project_id = 'gesture-detection-265519'
    model_id = 'ICN7380709295957999616'

    prediction_client = automl.PredictionServiceClient()

    # Get the full path of the model.
    model_full_id = prediction_client.model_path(
        project_id, 'us-central1', model_id
    )

    # Read the file.
    with open(file_path, 'rb') as content_file:
        content = content_file.read()


    image = automl.types.Image(image_bytes=content)
    payload = automl.types.ExamplePayload(image=image)

    # params is additional domain-specific parameters.
    # score_threshold is used to filter the result
    params = {'score_threshold': '0.5'}

    response = prediction_client.predict(model_full_id, payload, params)

    display_dict = {"ONE" : 1, "TWO" : 2, "THREE" : 3, "FOUR" : 4, "FIVE" : 5, "NONE" : 0}
    for result in response.payload:
        return display_dict[result.display_name]
    return 0
