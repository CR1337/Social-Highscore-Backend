FROM ubuntu:latest

# Install python3
RUN apt-get update
RUN apt-get install -y python3.5 python3-pip
RUN apt-get install ffmpeg libsm6 libxext6 -y

# Copy requirements.txt
COPY requirements.txt /opt/face_api/requirements.txt

# Install dependencies
RUN pip3 install -r /opt/face_api/requirements.txt

# Copy app directory
COPY . /opt/face_api

# Set default directory
ENV HOME /opt/face_api
WORKDIR /opt/face_api

# Expost port
EXPOSE 8080

# Copy models
# ADD models /root/.deepface/weights

# Command to run on start
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "face_api.wsgi"]
