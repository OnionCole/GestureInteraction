from google.cloud import automl

def gesture_detection(file_path):
    project_id = 'gesture-detection-265519'
    model_id = 'ICN7380709295957999616'
    #file_path = '1579420371.6331792 real_good.png'

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
    print('Prediction results:')
    for result in response.payload:
        print(u'Predicted class name: {}'.format(result.display_name))
        print(u'Predicted class score: {}'.format(result.classification.score))
