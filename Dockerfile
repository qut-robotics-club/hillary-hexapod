FROM balenalib/raspberry-pi2-debian:latest

RUN sudo apt update && sudo apt upgrade && sudo apt install wget bzip2

RUN useradd -m -g sudo pi
USER pi
WORKDIR /home/pi

RUN wget https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh

RUN bash Berryconda3-2.0.0-Linux-armv7l.sh -b
ENV PATH /home/pi/berryconda3/bin:${PATH}