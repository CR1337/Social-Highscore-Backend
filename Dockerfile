FROM python:3.8-slim-buster
WORKDIR /usr/src/api
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "api.py"]
