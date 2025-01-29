FROM python:3.12-alpine

RUN apk upgrade --no-cache

WORKDIR /mnt/retrogile

COPY ./ ./
RUN apk add --update alpine-sdk
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x ./run.sh
CMD [ "./run.sh" ]
