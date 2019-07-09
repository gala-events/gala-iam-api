FROM python:3.7-alpine as base

FROM base as builder
RUN apk add gcc libc-dev make

WORKDIR /install

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ADD ./src/api/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

FROM base
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY ./src/api ./


ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

EXPOSE 80

ENV MONGO_DB__HOST_URI="mongo"
ENV MONGO_DB__HOST_PORT="27017"

CMD ["uvicorn", "server:app", "--reload", "--host", "0.0.0.0", "--port", "80" ]
