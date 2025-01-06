FROM python:3.12-alpine

WORKDIR /mnt/retrogile

COPY ./ ./
RUN apk add --update alpine-sdk
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./api.py" ]
