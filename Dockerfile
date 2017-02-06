FROM python:2.7
ADD ./requirements.txt /src/requirements.txt
RUN cd /src && pip install -r requirements.txt
ADD . /src
WORKDIR /src
