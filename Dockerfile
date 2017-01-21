FROM ubuntu:16.04

RUN apt-get -y update

RUN apt-get install -y nodejs npm wget &&\
  npm install -g n &&\
  n latest &&\
  apt-get -y update

RUN apt-get install -y python-pip python-dev build-essential &&\
  pip install --upgrade pip &&\
  pip install --upgrade virtualenv && \
  pip install Flask &&\
  apt-get -y update


RUN mkdir /dist
WORKDIR /dist
EXPOSE 5000
ENV PORT=5000

ENTRYPOINT npm start
