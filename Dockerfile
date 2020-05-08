FROM python:2.7

COPY ./ /opt/dbod-api
COPY ./static/api.cfg /etc/apiato/apiato.cfg

WORKDIR /opt/dbod-api

RUN apt-get update -y && apt-get upgrade -y && pip install -r requirements.txt && python setup.py install && apt-get install -y libpq*

CMD ["bin/apiato"]
