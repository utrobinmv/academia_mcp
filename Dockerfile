# Dockerfile
# Use a Python image with uv pre-installed
FROM python:3.12.9-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install the project into `/app`
WORKDIR /app

# Runtime libs
RUN apt-get update && apt-get install -yq \
                build-essential \
                git-core \
                pkg-config \
                git-lfs \
                libtool \
                zlib1g-dev \
                libbz2-dev \
                automake \
                python3-dev \
                wget \
                curl \
                mc tmux \
                build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev \
                make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl libgtk2.0-dev \
                libjpeg-dev zlib1g-dev \ 
                curl git-core gcc make zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libssl-dev tk-dev libffi-dev liblzma-dev \ 
                python3-dev python3-venv ffmpeg libsm6 libxext6 openssl cargo \ 
				&& rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-latex-extra texlive-science && rm -rf /var/lib/apt/lists/*

COPY ./academia_mcp /app/academia_mcp
COPY ./tests /app/tests
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements-test.txt /app/requirements-test.txt

ARG DOCKER_USER_NAME=app_user

RUN useradd -mG cdrom,users,dip,plugdev -s /bin/bash $DOCKER_USER_NAME

RUN chown -R $DOCKER_USER_NAME:users /app

USER $DOCKER_USER_NAME

RUN python3 -m venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY ./check_proxy_list.py /app/check_proxy_list.py
