FROM ubuntu:latest
LABEL authors="batuh"

ENTRYPOINT ["top", "-b"]