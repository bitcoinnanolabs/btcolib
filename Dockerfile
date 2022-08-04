FROM python:3.7-alpine as base

ENV PYTHONDONTWRITEBYTECODE 1

RUN apk --no-cache update
RUN apk --no-cache add build-base
RUN apk --no-cache add libzmq
RUN apk --no-cache add zeromq-dev
RUN apk --no-cache add python3 
RUN apk --no-cache add python3-dev 
RUN apk --no-cache add musl-dev
RUN apk add --no-cache --update py3-pip
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
    

# Now multistage builds
FROM python:3.7-alpine


COPY --from=base /usr/local/lib/python3.7/site-packages/ /usr/local/lib/python3.7/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/
RUN apk --no-cache add libzmq
WORKDIR /code

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /code:$PYTHONPATH


COPY proxy.py /code/

ENTRYPOINT ["python3"]

CMD ["botsend.py"]