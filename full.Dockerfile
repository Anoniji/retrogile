FROM python:3.14-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        busybox \
        zlib1g && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /mnt/retrogile

COPY ./ ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD [ "sh", "-c", "python ./script.py" ]
