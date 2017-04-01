FROM python:latest
ENV PYTHONUNBUFFERED 1

ENV C_FORCE_ROOT true



ENV APP_ROOT /src
RUN mkdir /src
RUN mkdir /src/log

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
	git \
	vim \
	libpq-dev \
	gettext \
	libgeoip-dev && \
	pip3 install -U pip setuptools && \
   rm -rf /var/lib/apt/lists/*

COPY requirements.txt ${APP_ROOT}/requirements.txt
RUN pip3 install -r ${APP_ROOT}/requirements.txt