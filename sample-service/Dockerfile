FROM ubuntu:16.04
LABEL maintainer="Carlos Justiniano cjus@ieee.org"
EXPOSE 15000

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python" ]
CMD [ "service.py" ]
