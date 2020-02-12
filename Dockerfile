FROM alpine

RUN apk add curl

RUN curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh | sh