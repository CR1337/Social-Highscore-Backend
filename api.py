import warnings
warnings.filterwarnings("ignore")
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import base64
import json
from io import BytesIO

import tensorflow as tf
from deepface import DeepFace
from flask import Flask, jsonify, request
from PIL import Image

tf_version = int(tf.__version__.split(".")[0])
if tf_version == 2:
    import logging
    tf.get_logger().setLevel(logging.ERROR)
if tf_version == 1:
    graph = tf.get_default_graph()

app = Flask(__name__)

OK_200 = 200
BAD_REQUEST_400 = 400


def with_deepface(func):
    def wrapper(*args, **kwargs):
        global graph
        if tf_version == 1:
            with graph.as_default():
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper


@with_deepface
def detect_face(image):
    return DeepFace.detectFace(image)


@with_deepface
def analyze_face(image, actions):
    return DeepFace.analyze(image, actions)


@with_deepface
def verify_face(image0, image1):
    return DeepFace.verify(image0, image1)


def rotate_image(image, angle):
    if angle == 0:
        return image
    im = Image.open(BytesIO(base64.b64decode(image.split(",")[1])))
    im = im.rotate(angle)
    in_mem_file = BytesIO()
    im.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)
    img_bytes = in_mem_file.read()
    base64_encoded_result_bytes = base64.b64encode(img_bytes)
    base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
    return ",".join([image.split(",")[0], base64_encoded_result_str])


def determine_rotation_angle(image):
    for angle in [0, 90, 180, 270]:
        rotated_image = rotate_image(image, angle)
        try:
            detect_face(rotated_image)
        except ValueError:
            pass
        else:
            return {'angle': angle}
    raise ValueError()


def api_route(func):
    def wrapper():
        request_data = json.loads(request.data.decode(encoding='utf-8'))

        if 'job_id' not in request_data:
            return (
                jsonify({'success': False, 'error': "no job_id"}),
                BAD_REQUEST_400
            )
        else:
            job_id = request_data['job_id']

        result, code = func(request_data)

        result['job_id'] = job_id
        result['success'] = (code == OK_200)

        return jsonify(result), code
    return wrapper


@app.route('/', methods=['GET'], endpoint='index')
def index():
    return '<h1>Hello, world!</h1>', OK_200


@app.route('/analyze', methods=['POST'], endpoint='analyze')
@api_route
def analyze(request_data):
    angle = request_data.get('angle', 0)

    if 'img' not in request_data:
        return {'error': "no img"}, BAD_REQUEST_400
    image = rotate_image(request_data['img'], angle)

    actions = request_data.get(
        'actions', ['emotion', 'age', 'gender', 'race']
    )

    try:
        result = analyze_face(image, actions)
    except ValueError:
        return {'error': 'no face'}, BAD_REQUEST_400
    else:
        return result, OK_200


@app.route('/verify', methods=['POST'], endpoint='verify')
@api_route
def verify(request_data):
    angle = request_data.get('angle', 0)

    images = [None, None]
    for i, key in enumerate(['img0', 'img1']):
        if key not in request_data:
            return {'error': f"no img{i}"}, BAD_REQUEST_400
        images[i] = rotate_image(request_data[key], angle)

    try:
        result = verify_face(images[0], images[1])
    except ValueError:
        return {'error': 'no face'}, BAD_REQUEST_400
    else:
        return result, OK_200


@app.route('/determine-angle', methods=['POST'], endpoint='determine_angle')
@api_route
def determine_angle(request_data):
    if 'img' not in request_data:
        return {'error': "no img"}, BAD_REQUEST_400
    image = request_data['img']

    try:
        result = determine_rotation_angle(image)
    except ValueError:
        return {'error': 'no face'}, BAD_REQUEST_400
    else:
        return result, OK_200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
