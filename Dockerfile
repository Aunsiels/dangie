from python:3

RUN apt update -yqq \
    && apt upgrade -yqq \
    && rm -rf /var/lib/apt/lists/*  

RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN pip3 install \
    psycopg2 \
    waitress

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

EXPOSE 5000

RUN mkdir /logs && chmod -R 777 /logs

COPY ./dist/*.whl /

RUN pip3 install *.whl

CMD echo "Starting Server..." && waitress-serve --call 'dangie:create_app'
