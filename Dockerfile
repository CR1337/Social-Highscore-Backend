FROM python:3.8-slim-buster
WORKDIR /usr/src/api
RUN mkdir /usr/src/models
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install htop=2.2.0-1+b1 ffmpeg=7:4.1.8-0+deb10u1 libsm6=2:1.2.3-1 libxext6=2:1.3.3-1+b2 -y
RUN pip install -r requirements.txt
COPY api.py api.py
ADD models /root/.deepface/weights
CMD ["python3", "api.py"]
