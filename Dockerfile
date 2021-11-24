FROM python:3.8-slim-buster
WORKDIR /usr/src/api
#ENV FLASK_APP=api.py
#ENV FLASK_RUN_HOST=0.0.0.0
#Server will reload itself on file changes if in dev mode
#ENV FLASK_ENV=development 
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "api.py"]
