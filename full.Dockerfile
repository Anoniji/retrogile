FROM python:3.13-alpine

RUN apk upgrade --no-cache

WORKDIR /mnt/retrogile

COPY ./ ./
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x ./run.sh
CMD [ "./run.sh" ]
