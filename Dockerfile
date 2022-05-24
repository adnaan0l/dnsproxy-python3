# Alpine base image that contains python 3.9
FROM python:3.9-alpine

RUN apk update \
    && apk upgrade

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install -r requirements.txt

RUN mkdir logs
RUN touch logs/info.log
RUN touch logs/error.log

COPY src ./

EXPOSE 53/tcp 53/udp

ENTRYPOINT [ "python", "./proxyserver.py" ]
