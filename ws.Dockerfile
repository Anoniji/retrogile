FROM python:3.14-alpine

RUN apk upgrade --no-cache && \
    apk add --no-cache busybox

WORKDIR /mnt/retrogile

COPY ./ ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD [ "sh", "-c", "python ./ws.py --account_email \"$ACCOUNT_EMAIL\"" ]
