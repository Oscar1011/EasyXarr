ARG ALPINE_VER=3.13

FROM python:3.8-alpine3.15

RUN   cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
      echo "Asia/Shanghai" > /etc/timezone && \
      apk del tzdata
 
COPY ./requirements.txt .
RUN pip3 install --no-cache -r requirements.txt
