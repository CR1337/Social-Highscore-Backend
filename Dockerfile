FROM python:3.8-slim-buster
WORKDIR /usr/src/api
RUN mkdir /usr/src/models
ENV DEEPFACE_HOME /usr/src/models
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install -r requirements.txt
COPY api.py api.py
COPY models /usr/src/models/.deepface/weights
CMD ["python3", "api.py"]
