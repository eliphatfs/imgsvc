FROM python:3.9
COPY . /imgsvc
WORKDIR /imgsvc
RUN pip install -r requirements.txt
RUN pip install -e .
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
