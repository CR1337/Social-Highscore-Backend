# based on: https://github.com/serengil/deepface

import warnings
warnings.filterwarnings("ignore")

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

#------------------------------

from flask import Flask, jsonify, request, make_response

import argparse
import uuid
import json
import time
import base64
from io import BytesIO
from tqdm import tqdm
from PIL import Image

#------------------------------

import tensorflow as tf
tf_version = int(tf.__version__.split(".")[0])

#------------------------------

if tf_version == 2:
	import logging
	tf.get_logger().setLevel(logging.ERROR)

#------------------------------

from deepface import DeepFace

#------------------------------

app = Flask(__name__)

#------------------------------

if tf_version == 1:
	graph = tf.get_default_graph()

#------------------------------

def rotate_image(image, angle):
	im = Image.open(BytesIO(base64.b64decode(image.split(",")[1])))
	im = im.rotate(angle)
	in_mem_file = BytesIO()
	im.save(in_mem_file, format="JPEG")
	# reset file pointer to start
	in_mem_file.seek(0)
	img_bytes = in_mem_file.read()
	base64_encoded_result_bytes = base64.b64encode(img_bytes)
	base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
	return ",".join([image.split(",")[0], base64_encoded_result_str])


#Service API Interface

@app.route('/')
def index():
	return '<h1>Hello, world!</h1>'

@app.route('/analyze', methods=['POST'])
def analyze():

	global graph

	tic = time.time()
	req = request.get_json()
	trx_id = uuid.uuid4()



	#---------------------------

	if tf_version == 1:
		with graph.as_default():
			resp_obj, return_code = analyzeWrapper(req, trx_id)
	elif tf_version == 2:
		resp_obj, return_code = analyzeWrapper(req, trx_id)

	#---------------------------

	toc = time.time()

	resp_obj["trx_id"] = trx_id
	resp_obj["seconds"] = toc-tic

	return resp_obj, return_code

def analyzeWrapper(req, trx_id = 0):
	if "img" in list(req.keys()):
		raw_content = req["img"] #list

		# TODO: This needs a very good comment
		angle = 0 if 'angle' not in req else req['angle']
		raw_content = rotate_image(raw_content, angle)


	else:
		return jsonify({'success': False, 'error': 'you must pass an img object in your request'}), 205

	print("Analyzing instance")

	#---------------------------

	detector_backend = 'opencv'

	actions= ['emotion', 'age', 'gender', 'race']

	if "actions" in req:
		actions = req["actions"]


	#---------------------------
	resp_obj = {}
	try:
		resp_obj = DeepFace.analyze(raw_content, actions=actions)
		return resp_obj, 200
	except Exception as err:
		print("Exception: ", str(err))
		resp_obj = {'error': str(err)}
		return resp_obj, 205


@app.route('/verify', methods=['POST'])
def verify():

	global graph

	tic = time.time()
	req = request.get_json()
	trx_id = uuid.uuid4()

	resp_obj = jsonify({'success': False})

	if tf_version == 1:
		with graph.as_default():
			resp_obj, return_code = verifyWrapper(req, trx_id)
	elif tf_version == 2:
		resp_obj, return_code = verifyWrapper(req, trx_id)

	#--------------------------

	toc =  time.time()

	resp_obj["trx_id"] = trx_id
	resp_obj["seconds"] = toc-tic

	return resp_obj, return_code

def verifyWrapper(req, trx_id = 0):

	resp_obj = jsonify({'success': False})

	model_name = "VGG-Face"
	distance_metric = "cosine"
	detector_backend = "opencv"


	#----------------------

	if "img" in list(req.keys()):
		raw_content = req["img"] #list

		instance = []
		img1 = raw_content["img1"]; img2 = raw_content["img2"]

		angle = 0 if 'angle' not in req else req['angle']
		img1 = rotate_image(img1, angle)
		img2 = rotate_image(img2, angle)


		validate_img1 = False
		if len(img1) > 11 and img1[0:11] == "data:image/":
			validate_img1 = True

		validate_img2 = False
		if len(img2) > 11 and img2[0:11] == "data:image/":
			validate_img2 = True

		if validate_img1 != True or validate_img2 != True:
			return jsonify({'success': False, 'error': 'you must pass both img1 and img2 as base64 encoded string'}), 205

		instance.append(img1); instance.append(img2)

	else:
		return jsonify({'success': False, 'error': 'you must pass two img objects in your request'}), 205

	#--------------------------

	print("Verifying instance")
	#--------------------------

	try:
		resp_obj = DeepFace.verify(instance
			, model_name = model_name
			, distance_metric = distance_metric
			, detector_backend = detector_backend
		)

	except Exception as err:
		resp_obj = jsonify({'success': False, 'error': str(err)}), 205

	return resp_obj, 200


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)