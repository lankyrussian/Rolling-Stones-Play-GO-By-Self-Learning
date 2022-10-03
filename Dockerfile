# this docker file does not include all steps to setup the image
# see notion notes for additional steps
FROM ros:noetic

RUN apt-get update

RUN apt-get install -y bluez bluetooth

COPY docker_entrypoint.sh /docker_entrypoint.sh

ENTRYPOINT sh docker_entrypoint.sh
