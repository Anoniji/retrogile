FROM python:3.14-alpine

RUN apk upgrade --no-cache && \
    apk add --no-cache busybox

WORKDIR /mnt/retrogile

COPY ./ ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN chmod +x ./run.sh
CMD [ "sh", "-c", "./run.sh" ]
