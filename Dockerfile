FROM python:3.7.1

LABEL Author="Leslie E."
LABEL E-mail="leslie.etubo@gmail.com"
LABEL version="0.0.1b"

ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP "news.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY ./config.py /app/config.py
COPY ./config.cfg /app/config.cfg
COPY ./news.py /app/news.py
COPY ./app /app/app

RUN pip install --upgrade pip && \
    pip install virtualenv && \
    pip install -r ./requirements.txt

ADD . /app

EXPOSE 5000

CMD flask run --host=0.0.0.0
# docker sytem prune (to free all used space)
# docker ps (to see all docker processes)
# docker stop [container_name] (to stop a particular container)
# docker run -d --name [sweet name for your container] -p 5000:5000 news_app (to run app in docker)
# docker attach [detached hash e.g a043d0f......]
# docker ps -a(to see running container)
# docker exec (to operate on a file in your docker container)