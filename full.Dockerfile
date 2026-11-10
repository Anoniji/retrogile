FROM python:3.14-slim

RUN apk upgrade --no-cache && \
    apk add --no-cache busybox && \
    apk add --no-cache zlib-ng && \
    apk add --no-cache --clean-protected zlib-ng-compat

WORKDIR /mnt/retrogile

COPY ./ ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD [ "sh", "-c", "python ./script.py" ]
