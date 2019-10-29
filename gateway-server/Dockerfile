FROM python:3.6

MAINTAINER Michael Ghen "admin@reachtechnologies.net"

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "flask" ]

CMD [ "run", "--host=0.0.0.0"]
