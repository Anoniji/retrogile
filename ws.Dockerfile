FROM python:3.13-alpine

RUN apk upgrade --no-cache

WORKDIR /mnt/retrogile

COPY ./ ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./ws.py" ]
