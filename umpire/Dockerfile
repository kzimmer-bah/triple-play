FROM python:3.7-alpine as base

FROM base as builder
RUN apk --no-cache add --update alpine-sdk

RUN mkdir /install
WORKDIR /install

COPY umpire/requirements.txt /requirements.txt

RUN pip install --prefix="/install" -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY ./ /app

WORKDIR /app

CMD python -m umpire.umpire