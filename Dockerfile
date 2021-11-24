FROM python:3.8-slim-buster
WORKDIR /usr/src/api
RUN mkdir /usr/src/models
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install -r requirements.txt
COPY api.py api.py
ADD models /root/.deepface/weights
CMD ["python3", "api.py"]
