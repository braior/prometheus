FROM python:3.8-slim-buster

# Copy the python source
COPY exporter /exporter

WORKDIR /exporter

RUN pip3 install -r requirements.txt

CMD ["python3", "manager.py"]