FROM ubuntu:16.04

RUN apt-get -y update

# for me
RUN apt-get install -y nodejs npm wget &&\
  npm install -g n &&\
  n latest &&\
  apt-get -y update

# for python
RUN apt-get install -y python-pip python-dev build-essential &&\
  pip install --upgrade pip &&\
  pip install --upgrade virtualenv && \
  apt-get -y update

# for postgres
RUN apt-get install -y libpq-dev

# for the server
RUN pip install Flask &&\
  pip install flask-login &&\
  pip install psycopg2

VOLUME /dist
WORKDIR /dist
EXPOSE 5000
ENV PORT=5000

ENTRYPOINT python init.py
