FROM python:3.10

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /izde2

COPY ./requirements.txt /izde2/

RUN sed -i '/twisted-iocpsupport/d' /izde2/requirements.txt && \
    pip install -r /izde2/requirements.txt

ADD . /izde2/

RUN python src/manage.py collectstatic --noinput
RUN python src/manage.py makemigrations

EXPOSE 8000
