FROM ubuntu

RUN apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    git \
    libgl1-mesa-dev \
    libgl1-mesa-glx \
    libglew-dev \
    libosmesa6-dev \
    software-properties-common \
    net-tools \
    vim \
    virtualenv \
    wget \
    xpra \
    xserver-xorg-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#RUN DEBIAN_FRONTEND=noninteractive add-apt-repository --yes ppa:deadsnakes/ppa && apt-get update
#RUN DEBIAN_FRONTEND=noninteractive apt-get install --yes python3.6-dev python3.6 python3-pip
#RUN virtualenv --python=python3.6 env
#
#RUN rm /usr/bin/python
#RUN ln -s /env/bin/python3.6 /usr/bin/python
#RUN ln -s /env/bin/pip3.6 /usr/bin/pip
#RUN ln -s /env/bin/pytest /usr/bin/pytest

RUN curl -o /usr/local/bin/patchelf https://s3-us-west-2.amazonaws.com/openai-sci-artifacts/manual-builds/patchelf_0.9_amd64.elf \
    && chmod +x /usr/local/bin/patchelf

ENV LANG C.UTF-8

ENV LD_LIBRARY_PATH /root/.mujoco/mujoco210/bin:${LD_LIBRARY_PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib64:${LD_LIBRARY_PATH}

# Copy over just requirements.txt at first. That way, the Docker cache doesn't
# expire until we actually change the requirements.
COPY ./mujoco_py /mujoco_py
COPY ./requirements.txt /mujoco_py/
COPY ./requirements.dev.txt /mujoco_py/
RUN apt-get update -q
RUN cd /mujoco_py && python3 -m pip install --no-cache-dir -r requirements.txt
RUN cd /mujoco_py && python3 -m pip install --no-cache-dir -r requirements.dev.txt

RUN cd /mujoco_py && python3 setup.py install

ADD . /rspg
COPY .mujoco /root/.mujoco

WORKDIR /rspg

# pathfinder
RUN apt-get update -q
RUN apt-get install libmosquitto-dev mosquitto-dev mosquitto -y
RUN cd /rspg/pathplanning && make ; cd ..
# go board
RUN python3 -m pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
# simulator
RUN python3 -m pip install paho-mqtt gym tqdm
#RUN #python -m pip install mujoco-py paho-mqtt gym
#RUN #apt install libosmesa6-dev libgl1-mesa-glx libglfw3 -y
#RUN #ln -s /usr/lib/x86_64-linux-gnu/libGL.so.1 /usr/lib/x86_64-linux-gnu/libGL.so
RUN chmod +x /rspg/playgo.sh /rspg/goboard/src/playgo.py /rspg/pathplanning/PathPlanner
# CMD mosquitto -d && xhost local:root && /rspg/pathplanning/PathPlanner
ENTRYPOINT ["./playgo.sh"]