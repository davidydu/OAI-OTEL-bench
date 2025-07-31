# You can use most Debian-based base images
FROM ubuntu:22.04
FROM python:3.11-slim
# Install dependencies and customize sandbox
RUN pip install browser-use==0.4.5
RUN pip install --upgrade --force-reinstall --no-cache-dir jupyter
RUN pip install logfire
RUN pip install lmnr