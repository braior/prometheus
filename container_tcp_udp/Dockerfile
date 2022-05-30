FROM python:3.8-slim-buster

# Copy the python source
COPY exporter /exporter

WORKDIR /exporter
RUN groupadd -g 1000 exporter && \
   useradd -u 1000 -g 1000 -G 0 -d /home/exporter exporter && \
   chmod 0755 /exporter && chgrp 0 /exporter
RUN pip3 install -r requirements.txt

USER exporter

CMD ["python3", "manager.py"]