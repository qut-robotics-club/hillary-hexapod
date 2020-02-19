FROM balenalib/raspberry-pi2-debian:latest

RUN sudo apt update && sudo apt upgrade && sudo apt install wget bzip2 libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev

RUN useradd -m -g sudo pi
USER pi
WORKDIR /home/pi

RUN wget https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh

RUN bash Berryconda3-2.0.0-Linux-armv7l.sh -b
ENV PATH /home/pi/berryconda3/bin:${PATH}

CMD 